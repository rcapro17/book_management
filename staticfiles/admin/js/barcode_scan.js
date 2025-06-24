document.addEventListener('DOMContentLoaded', function() {
    const isbnInput = document.getElementById('isbn-input');
    
    isbnInput.addEventListener('input', function() {
      // Ensure ISBN length is 13 characters (valid ISBN length for ISBN-13)
      if (isbnInput.value.length === 13) {
        // Make the API call to fetch book information using the entered ISBN
        fetch(`/admin/library/book/fetch-book-info/?isbn=${isbnInput.value}`)
          .then(response => response.json())
          .then(data => {
            if (data.title) {
              // Populate the other fields if data is returned
              document.getElementById('id_title').value = data.title;
              document.getElementById('id_author').value = data.author;
              document.getElementById('id_publisher').value = data.publisher;
              document.getElementById('id_description').value = data.description;
  
              // Optional: If cover image exists, display it
              if (data.cover) {
                document.getElementById('book-cover').innerHTML = `<img src="${data.cover}" width="50" height="75" />`;
              }
            } else {
              alert('Book not found.');
            }
          })
          .catch(error => {
            console.error('Error fetching book data:', error);
            alert('Error fetching book data.');
          });
      }
    });
  });
  