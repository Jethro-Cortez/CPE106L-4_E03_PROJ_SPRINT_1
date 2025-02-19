function listBooks() {
    fetch('/books')
        .then(response => response.json())
        .then(data => {
            const bookList = document.getElementById('book-list');
            bookList.innerHTML = '';
            data.forEach(book => {
                const li = document.createElement('li');
                li.textContent = `${book.title} by ${book.author} (${book.year}) - ${book.is_available ? 'Available' : 'Not Available'}`;
                bookList.appendChild(li);
            });
        });
}

function borrowBook() {
    // Implement the borrow book functionality
}

function returnBook() {
    // Implement the return book functionality
}

function provideFeedback() {
    // Implement the provide feedback functionality
}

function requestBook() {
    // Implement the request book functionality
}