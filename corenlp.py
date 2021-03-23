import multiprocessing as mp
import queue
import spacy
from typing import Dict, List, Tuple, Optional
from subpack.token import Token
nlp = spacy.load('de_core_news_lg', disable=['ner', 'parser', 'textcat', 'attribute_ruler']) #keep only tagger, lemmatizer, and module for word embedding


def _corenlp_server(classpath: str, properties: Dict[str, str], input_queue: mp.Queue, output_queue: mp.Queue):
	# Imports are inside function because pyjnius is ugly

	while True:
		job = input_queue.get()
		if job is None:
			break

		job_id, text, offset = job

		if text == "":
			output_queue.put((job_id, []))
			continue

		reconstructed_text = ""
		after = ""
		sentences = []
		sentence_tokens = []
		doc = nlp(text)
		for token in doc:
			original_text = token.text
			lemma = token.lemma_
			pos = token.pos_
			whitespace = token.whitespace_
			# start and end index are not used because they may be different from Python's string indexes.
			#     print(original_text)
			#     print(lemma)
			#     print(pos)
			begin = len(reconstructed_text) + offset
			reconstructed_text += original_text + whitespace
			end = len(reconstructed_text) + offset

			token_object = Token(
				start=begin,
				end=end,
				value=original_text,
				pos=pos,
				lemma=lemma,
				before=" ",
				after=" "
			)

			sentence_tokens.append(token_object)
		#     print(sentence_tokens)
		sentences.append(sentence_tokens)
		# print(sentences)
		# print(reconstructed_text)

		if reconstructed_text != text:
			print("Reconstructed Text didnt match text")
			output_queue.put((job_id, None))
		else:
			output_queue.put((job_id, sentences))


class CoreNlpBridge:
	"""
	Bridge between CoreNLP (Java) and Python.
	"""

	class TokenizationError(Exception):
		pass

	def __init__(self, classpath: str, properties: Optional[Dict[str, str]] = None, process_count: Optional[int] = None):
		"""
		Initializes CoreNLP bridge.

		:param classpath: Path to CoreNLP Java classes. e.g. "./corenlp/*"
		:param properties: Dict containing properties for CoreNLP. e.g. {"annotators": "tokenize,ssplit,pos,lemma"}
		:param process_count: Number of processes used for tokenization. Uses CPU count if None.
		"""
		assert classpath is not None
		assert process_count is None or process_count > 0

		if process_count is None:
			process_count = mp.cpu_count()

		if properties is None:
			properties = {
				"annotators": "tokenize,ssplit,pos,lemma",
				"tokenize.options": "untokenizable=noneKeep,invertible=true,ptb3Escaping=false",
				"tokenize.language": "en"
			}

		self.in_queue = mp.Queue(process_count)
		self.out_queue = mp.Queue(process_count)

		corenlp_processes = []
		args = (classpath, properties, self.in_queue, self.out_queue)

		for i in range(process_count):
			corenlp_process = mp.Process(target=_corenlp_server, args=args)
			corenlp_process.start()
			corenlp_processes.append(corenlp_process)

		self.corenlp_processes = corenlp_processes

	def close(self):
		"""
		Closes bridge. Call this method after you're done or use a `with` statement.
		"""
		in_queue = self.in_queue
		corenlp_processes = self.corenlp_processes

		self.corenlp_processes = None
		self.in_queue = None
		self.out_queue = None

		for _ in range(len(corenlp_processes)):
			in_queue.put(None)

		for corenlp_process in corenlp_processes:
			corenlp_process.join()

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.close()
		return False

	def tokenize(self, paragraphs: List[Tuple[int, str]]) -> List[List[List[Token]]]:
		"""
		Tokenizes text and splits it into sentences.

		:param paragraphs: List of paragraphs. Each paragraph is a tuple containing offset and text.
		:return: List of paragraphs. Each paragraph is a list of sentences. Each sentence is a list of tokens of type Token.
		"""

		assert self.corenlp_processes is not None

		remaining_jobs = []
		for paragraph_index in range(len(paragraphs)):
			offset, text = paragraphs[paragraph_index]
			remaining_jobs.append((paragraph_index, text, offset))

		output = []
		while True:
			while len(remaining_jobs) > 0:
				next_job = remaining_jobs.pop(0)
				try:
					self.in_queue.put(next_job, block=False)
				except queue.Full:
					remaining_jobs.insert(0, next_job)
					break

			paragraph_index, sentences = self.out_queue.get()
			if sentences is None:
				raise CoreNlpBridge.TokenizationError()

			output.append((paragraph_index, sentences))

			if len(output) == len(paragraphs):
				break

		return list(map(lambda x: x[1], sorted(output, key=lambda x: x[0])))
