class Document:
    def __init__(self, page_content, metadata=None):
        self.page_content = page_content
        self.metadata = metadata or {}


class RecursiveCharacterTextSplitter:
    def __init__(self, chunk_size=800, chunk_overlap=200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = ["\n\n", "\n", " ", ""]

    def split_text(self, text):
        return self._split_text(text, self.separators)

    def _split_text(self, text, separators):
        final_chunks = []
        separator = separators[-1]
        new_separators = []
        for i, s in enumerate(separators):
            if s == "":
                separator = s
                break
            if s in text:
                separator = s
                new_separators = separators[i + 1:]
                break

        if separator:
            splits = text.split(separator)
        else:
            splits = list(text)

        good_splits = []
        for s in splits:
            if len(s) < self.chunk_size:
                good_splits.append(s)
            else:
                if good_splits:
                    merged = self._merge_splits(good_splits, separator)
                    final_chunks.extend(merged)
                    good_splits = []
                if not new_separators:
                    final_chunks.append(s)
                else:
                    other_info = self._split_text(s, new_separators)
                    final_chunks.extend(other_info)

        if good_splits:
            merged = self._merge_splits(good_splits, separator)
            final_chunks.extend(merged)

        return final_chunks

    def _merge_splits(self, splits, separator):
        docs = []
        current_doc = []
        total = 0
        for s in splits:
            if total + len(s) + (len(separator) if len(current_doc) > 0 else 0) > self.chunk_size:
                if current_doc:
                    docs.append(separator.join(current_doc))
                    while total > self.chunk_overlap or (
                        total + len(s) + (len(separator) if len(current_doc) > 0 else 0) > self.chunk_size and total > 0
                    ):
                        total -= len(current_doc[0]) + (len(separator) if len(current_doc) > 1 else 0)
                        current_doc.pop(0)
            current_doc.append(s)
            total += len(s) + (len(separator) if len(current_doc) > 1 else 0)
        
        if current_doc:
            docs.append(separator.join(current_doc))
        return docs

    def split_documents(self, documents):
        new_docs = []
        for doc in documents:
            chunks = self.split_text(doc.page_content)
            for chunk in chunks:
                new_docs.append(Document(page_content=chunk, metadata=doc.metadata.copy()))
        return new_docs
