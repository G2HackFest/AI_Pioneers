document.getElementById('classifyBtn').addEventListener('click', function() {
    const file = document.getElementById('wasteImage').files[0];
    if (!file) {
        alert('Please select an image first!');
        return;
    }

    // Mock classification (replace with actual API call)
    const categories = ['Recyclable', 'Compostable', 'Non-Recyclable'];
    const randomCategory = categories[Math.floor(Math.random() * categories.length)];
    
    document.getElementById('result').innerHTML = `
        <h4>Classification Result</h4>
        <p><strong>Category:</strong> ${randomCategory}</p>
        <p><strong>Confidence:</strong> ${(Math.random() * 100).toFixed(2)}%</p>
        <p><strong>Disposal Tip:</strong> ${getDisposalTip(randomCategory)}</p>
    `;
});

function getDisposalTip(category) {
    const tips = {
        'Recyclable': 'Rinse containers before recycling',
        'Compostable': 'Remove non-organic attachments',
        'Non-Recyclable': 'Dispose in general waste bin'
    };
    return tips[category];
}                                        