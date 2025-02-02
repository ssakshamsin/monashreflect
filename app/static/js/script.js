function filterUnits() {
    const searchBar = document.getElementById('searchBar');
    const filter = searchBar.value.toLowerCase();
    const unitCards = document.querySelectorAll('.unit-card');
  
    unitCards.forEach(card => { // for each card 
      const code = card.dataset.code.toLowerCase(); //we get its code and name 
      const name = card.dataset.name.toLowerCase();
      const faculty = card.dataset.faculty.toLowerCase();
      if (code.includes(filter) || name.includes(filter) || faculty.includes(filter)) { //and check if it includes what we have typed
        card.style.display = ''; // if it is display
      } else {
        card.style.display = 'none'; // do not display 
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