from repository.books import BookRepository


class BookService:
    def __init__(self, db):
        self.repo = BookRepository(db)

    def get_all_books(
        self,
        status=None,
        author=None,
        sort_by=None,
        sort_order="asc",
        limit=10,
        offset=0,
    ):
        return self.repo.get_all(
            status=status,
            author=author,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=offset,
        )

    def get_book_by_id(self, book_id):
        return self.repo.get_by_id(book_id)

    def create_book(self, book_data):
        return self.repo.create(book_data)

    def update_book(self, book_id, book_data):
        return self.repo.update(book_id, book_data)

    def delete_book(self, book_id):
        return self.repo.delete(book_id)
