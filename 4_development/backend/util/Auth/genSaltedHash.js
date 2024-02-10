// Usage: node genSaltedHash.js word
// Output: word, hash, salt

const bcrypt = require('bcrypt');

async function genSaltedHash(word) {
    bcrypt.genSalt(10).then(salt => {
        bcrypt.hash(word, salt).then(hash => {
            console.log(`input: ${word} , output: ${hash}`)
        });
    });
}

genSaltedHash(process.argv[2]);