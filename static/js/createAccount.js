function reset() {
    document.getElementById("myForm").reset();
    }

// var err = "{{err}}"

// if (performance.navigation.type === 2) {
//     console.log("hi");
//     document.getElementById("errorMessage").style.display = "none";
//   }
// if (err=="true"){
//     document.getElementById("errorMessage").style.display = "block";
// }




function areFieldsUnique(){
    const sqlite3 = require('sqlite3').verbose();

    // Open the database connection
    const db = new sqlite3.Database('/users.db');

    // Define the text field you want to check
    const textField = 'example text';

    // Construct the SQL query to check if the text field exists
    const query = `SELECT COUNT(*) AS count FROM users WHERE text_field = ?`;

    // Execute the query and check the result
    db.get(query, [textField], (err, row) => {
    if (err) {
        console.error(err.message);
    } else {
        if (row.count > 0) {
        console.log(`The text field "${textField}" already exists in the database.`);
        db.close();
        return false;
        } else {
        console.log(`The text field "${textField}" does not exist in the database.`);
        db.close();
        return true;
        }
    }
    });    
}

const form = document.getElementById("accountCreateForm")
const submitBtn = document.getElementById("submitBtn")

submitBtn.addEventListener('click', (event) => {
    if (!areFieldsUnique()) {
      event.preventDefault(); // prevent form submission
      alert('Form cannot be submitted.'); // display alert message
    }
  });
