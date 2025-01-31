function filterUnits() {
    const searchBar = document.getElementById('searchBar');
    const filter = searchBar.value.toLowerCase();
    const unitCards = document.querySelectorAll('.unit-card');
  
    unitCards.forEach(card => {
      const code = card.dataset.code.toLowerCase();
      const name = card.dataset.name.toLowerCase();
      if (code.includes(filter) || name.includes(filter)) {
        card.style.display = '';
      } else {
        card.style.display = 'none';
      }
    });
  }


  // Initialize vote counts
let votes = {
  good: 100, // Initial Good votes
  bad: 20,   // Initial Bad votes
};


// Function to update the UI with initial votes
function initializeUI() {
  const totalVotes = votes.good + votes.bad;

  document.getElementById('goodVotes').textContent = votes.good;
  document.getElementById('badVotes').textContent = votes.bad;
  document.getElementById('totalVotes').textContent = totalVotes;

  const goodPercentage = (votes.good / totalVotes) * 100 || 50;
  const badPercentage = (votes.bad / totalVotes) * 100 || 50;

  document.getElementById('goodBar').style.width = `${goodPercentage}%`;
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