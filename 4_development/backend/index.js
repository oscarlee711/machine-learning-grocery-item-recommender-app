//use express
const express = require('express');
const app = express();
const bodyParser = require('body-parser'); //middleware used to handle request bodies
const errorController = require('./controllers/error-controller'); //error handling
const mongoose = require('mongoose'); //used to access the MongoDB
require("dotenv").config(); //used to access the .env file easily

//setup keys
const fs = require('fs');
process.env.PRIVATE_KEY = fs.readFileSync('./util/Auth/rsa_private.pem', 'utf8');
process.env.PUBLIC_KEY = fs.readFileSync('./util/Auth/rsa_public.pem', 'utf8');

//setup passport
const passport = require('passport');
require('./util/Auth/passport.js')(passport);

//routes from /routes/
const shopRoute = require('./routes/shop-route');
const itemRoute = require('./routes/item-route');
const receiptRoute = require('./routes/receipt-route')
const ocrRoute = require('./routes/ocr-route');
const userRoute = require('./routes/user-route');
const viewReceiptRoute = require('./routes/viewReceipt-route');

//port to listen on from .ENV file
const ports = process.env.PORT || 3000;

//use body parser and ejs
app.use(bodyParser.urlencoded({ extended: false }))
app.use(bodyParser.json())
app.set("view engine", "ejs");

//connect to MongoDB
mongoose.connect(process.env.MONGO_URL,
    { useNewUrlParser: true, useUnifiedTopology: true }, err => {
        if (err)
            console.log(err.message)
        else
            console.log('connected to MongoDB')
    });

app.use(express.json());
app.use((err, req, res, next) => {
    res.status(400).json({ status: 400, message: "Invalid JSON format" })
});

// Authenticates supplied token and provides custom error messages
function authenticateToken(req, res, next) {
    console.log(req.originalUrl);
    // Allow login/register attempt as a token has not yet been granted
    if (req.originalUrl === '/user/login' || req.originalUrl === '/user/create') {
        next();
        return;
    }

    passport.authenticate('jwt', { session: false }, (error, user_id, info) => {
        if (user_id == false) {
            if (info.name === "TokenExpiredError") return res.status(400).json({ status: 400, message: "Authentication Failure: Expired token" });
            if (info.name === "JsonWebTokenError") return res.status(400).json({ status: 400, message: "Authentication Failure: Invalid token" });
            if (info.name === "Error") return res.status(400).json({ status: 400, message: "Authentication Failure: Missing token" });
            return res.status(400).json({ status: 400, message: "Authentication Failure: General" });
        }
        req.user_id = user_id;
        console.log("user_id: " + user_id);
        next();
    })(req, res);
}

//endpoints from routes.
app.use('/shop', authenticateToken, shopRoute);
app.use('/item', authenticateToken, itemRoute);
app.use('/receipt', authenticateToken, receiptRoute);
app.use('/ocr', authenticateToken, ocrRoute);
app.use('/user', authenticateToken, userRoute);
app.use('/view', authenticateToken, viewReceiptRoute);

//Default request (display no error)
app.use((req, res) => {
    res.sendStatus(404);
});

//error handling if no route is present etc
app.use(errorController.get404);
app.use(errorController.get500);

//start listening
app.listen(ports, () => console.log('listening...'));

//open browser, uncomment the three lines below for auto open browser
//const open = require('open');
//const res = require('express/lib/response');
//open('http://localhost:3000/');