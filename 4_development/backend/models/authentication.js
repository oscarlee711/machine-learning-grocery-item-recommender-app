const mongoose = require("mongoose");
const Schema = mongoose.Schema;

const VerificationSchema = new Schema({
    OTP: String,
    CreatedAt: Date,
    ExpiresAt: Date,
});

const OTP = mongoose.model("OTP", VerificationSchema);

module.exports = VerificationSchema;