document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const resultsBtn = document.getElementById('results-btn');
    const options = document.querySelectorAll('input[name="option"]');
    const inputBoxesContainer = document.getElementById('input-boxes');

    // Add event listeners to options
    options.forEach(option => {
        option.addEventListener('change', function() {
            updateInputBoxes();
        });
    });

    // Function to update input boxes based on selected options
    function updateInputBoxes() {
        inputBoxesContainer.innerHTML = '';
        options.forEach(option => {
            if (option.checked) {
                const inputBox = document.createElement('div');
                inputBox.innerHTML = `
                    <label for="${option.value}-input">${option.value.charAt(0).toUpperCase() + option.value.slice(1)}:</label>
                    <input type="number" id="${option.value}-input" name="${option.value}-input" value="${option.dataset.default}" step="0.1">
                `;
                inputBoxesContainer.appendChild(inputBox);
            }
        });
    }

    // Event listener for results button
    resultsBtn.addEventListener('click', function() {
        // Get selected options
        const selectedOptions = Array.from(options)
            .filter(option => option.checked);

        // Check if at least one option is selected
        if (selectedOptions.length === 0) {
            alert('Please select at least one option.');
            return;
        }

        // Generate query parameters for selected options
        const queryParams = selectedOptions.map(option => {
            const inputValue = document.getElementById(`${option.value}-input`).value;
            return `option=${option.value}&${option.value}Value=${inputValue}`;
        });
        
        // Redirect to results page with query parameters
        window.location.href = `/results?${queryParams.join('&')}`;
    });
});