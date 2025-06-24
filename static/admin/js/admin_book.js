// library/static/js/admin_book.js

(function($) {
    $(document).ready(function() {
        // Listen for the click event on the "Fetch Data" button
        $('#book-list').on('click', '#fetch-book', function() {
            var isbn = $(this).data('isbn');
            
            $.ajax({
                url: '/admin/library/fetch-book-info/',  // This is the custom URL defined in `BookAdmin`
                method: 'GET',
                data: { isbn: isbn },
                success: function(response) {
                    if (response.error) {
                        alert(response.error);
                    } else {
                        // Populate fields in the admin panel form with the API data
                        alert('Book data fetched successfully!');
                        // Here you would trigger an event to populate the form, e.g.:
                        // $('#id_title').val(response.title);
                        // $('#id_author').val(response.author);
                        // etc.
                    }
                },
                error: function() {
                    alert('Error fetching book data.');
                }
            });
        });
    });
})(django.jQuery);
