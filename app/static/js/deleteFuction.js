
function deleteBooking(user_id, booking_id) {
      if (confirm('Are you sure you want to delete this reservation?')) {
          fetch(`/user/${user_id}/delete/${booking_id}`, {
              method: 'DELETE',
              headers: {
                  'Content-Type': 'application/json',
              },
         
          })
          .then(response => {
              if (response.ok) {
                  alert('Reservation deleted successfully.');
                  window.location.reload();
              } else {
                  alert('Error deleting reservation.');
              }
          })
          .catch(error => {
              console.error('Error:', error);
              alert('Error in the request.');
          });
      }
}
