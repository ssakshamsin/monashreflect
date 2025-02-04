document.addEventListener('DOMContentLoaded', function() {
  const searchBar = document.getElementById('searchBar');
  const unitsGrid = document.getElementById('unitsGrid');
  let paginationContainer = document.querySelector('.pagination');
  
  // Create pagination container if it doesn't exist
  if (!paginationContainer) {
    paginationContainer = document.createElement('div');
    paginationContainer.className = 'pagination';
    unitsGrid.parentNode.insertBefore(paginationContainer, unitsGrid.nextSibling);
  }

  function renderUnit(unit) {
    const unitCard = document.createElement('div');
    unitCard.classList.add('unit-card');
    unitCard.dataset.code = unit.code;
    unitCard.dataset.name = unit.name;
    unitCard.dataset.faculty = unit.faculty;

    unitCard.innerHTML = `
        <h2>${unit.code} - ${unit.name}</h2>
        <p>${unit.faculty}</p>
        <a href="unit/${unit.code}">View Reviews</a>
    `;

    return unitCard;
  }

  function fetchResults(query, page = 1) {
    // Choose endpoint based on whether there's a search query
    const endpoint = query ? `/api/search?query=${query}&page=${page}` : `/units?page=${page}`;
    
    fetch(endpoint, {
      headers: {
        'Accept': 'application/json'
      }
    })
    .then(response => {
      if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
        // Clear previous results
        unitsGrid.innerHTML = '';
        
        // Display units
        if (data.units && data.units.length > 0) {
            data.units.forEach(unit => {
                unitsGrid.appendChild(renderUnit(unit));
            });
        } else {
            unitsGrid.innerHTML = '<p>No units found.</p>';
        }

        // Handle pagination data from both endpoints
        const totalPages = data.total_pages || data.pages || 1;
        const currentPage = data.current_page || data.page || 1;
        
        // Only show pagination if there are multiple pages
        if (totalPages > 1) {
            updatePagination(totalPages, currentPage, query);
        } else {
            paginationContainer.innerHTML = '';
        }
    })
    .catch(error => {
        console.error('Error fetching results:', error);
        unitsGrid.innerHTML = '<p>Error loading units. Please try again.</p>';
    });
}
  
  function updatePagination(totalPages, currentPage, query) {
    paginationContainer.innerHTML = '';
    
    const paginationContent = document.createElement('div');
    paginationContent.className = 'pagination-content';

    // Previous button
    if (currentPage > 1) {
        const prevButton = document.createElement('button');
        prevButton.className = 'pbtn';
        prevButton.innerHTML = '&laquo; Previous';
        prevButton.addEventListener('click', () => fetchResults(query, currentPage - 1));
        paginationContent.appendChild(prevButton);
    }

    // Page numbers
    for (let i = 1; i <= totalPages; i++) {
        if (
            i <= 2 || // First two pages
            i > totalPages - 2 || // Last two pages
            (i >= currentPage - 1 && i <= currentPage + 1) // Pages around current
        ) {
            const pageButton = document.createElement('button');
            pageButton.className = `pbtn ${i === currentPage ? 'active' : ''}`;
            pageButton.textContent = i;
            pageButton.addEventListener('click', () => fetchResults(query, i));
            paginationContent.appendChild(pageButton);
        } else if (paginationContent.lastElementChild?.textContent !== '...') {
            const ellipsis = document.createElement('span');
            ellipsis.className = 'ellipsis';
            ellipsis.textContent = '...';
            paginationContent.appendChild(ellipsis);
        }
    }

    // Next button
    if (currentPage < totalPages) {
        const nextButton = document.createElement('button');
        nextButton.className = 'pbtn';
        nextButton.innerHTML = 'Next &raquo;';
        nextButton.addEventListener('click', () => fetchResults(query, currentPage + 1));
        paginationContent.appendChild(nextButton);
    }

    paginationContainer.appendChild(paginationContent);
}

  // Handle search input
  let searchTimeout;
  searchBar.addEventListener('input', function() {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
          const query = searchBar.value;
          fetchResults(query, 1);  // Reset to page 1 when searching
      }, 300);
  });

  // Initial load - fetch first page
  fetchResults('', 1);
});
  // Initialize vote counts
let votes = {
  good: 100, // Initial Good votes
  bad: 20,   // Initial Bad votes
};


// Function to update the UI with initial votes
function initializeUI() {
  const totalVotes = votes.good + votes.bad;

  document.getElementById('goodVotes').textContent = votes.good; // setting text
  document.getElementById('badVotes').textContent = votes.bad;
  document.getElementById('totalVotes').textContent = totalVotes;

  const goodPercentage = (votes.good / totalVotes) * 100 || 50; // to counter the nan case of 0 votes 
  const badPercentage = (votes.bad / totalVotes) * 100 || 50;

  document.getElementById('goodBar').style.width = `${goodPercentage}%`; // setting size
  document.getElementById('badBar').style.width = `${badPercentage}%`;
}

// Function to handle voting
function vote(option) {
  // Increment the selected option's vote count
  votes[option]++;

  // Update the total votes
  const totalVotes = votes.good + votes.bad;

  document.getElementById('goodVotes').textContent = votes.good;
  document.getElementById('badVotes').textContent = votes.bad;
  document.getElementById('totalVotes').textContent = totalVotes;

  // Calculate percentages
  const goodPercentage = (votes.good / totalVotes) * 100 || 50;
  const badPercentage = (votes.bad / totalVotes) * 100 || 50;

  // Update the width of the bars
  document.getElementById('goodBar').style.width = `${goodPercentage}%`;
  document.getElementById('badBar').style.width = `${badPercentage}%`;
}

// Initialize the UI with initial votes
initializeUI();