const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
fetch('/some-endpoint', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': csrfToken,
    },
    body: JSON.stringify(data),
});
