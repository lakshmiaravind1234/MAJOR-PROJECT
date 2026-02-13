// models/User.js
const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');

const UserSchema = new mongoose.Schema({
    username: {
        type: String,
        required: true,
        unique: true
    },
    email: {
        type: String,
        required: true,
        unique: true
    },
    password: {
        type: String,
        required: true
    },
    createdAt: {
        type: Date,
        default: Date.now
    },
    // ⭐ UPDATED FIELD for Automatic Prompt-Specific Consistency
    promptSpecificSeeds: {
        type: Map,
        of: String,
        default: () => new Map() // Use a function to ensure a fresh map
    }
});

UserSchema.pre('save', async function(next) {
    if (!this.isModified('password')) {
        return;// Use return here
    }
    try {
        const salt = await bcrypt.genSalt(10);
        this.password = await bcrypt.hash(this.password, salt);
        
    } catch (err) {
        throw err;
    }
});
// Method to compare passwords
UserSchema.methods.matchPassword = async function(enteredPassword) {
    return await bcrypt.compare(enteredPassword, this.password);
};

module.exports = mongoose.model('User', UserSchema);


