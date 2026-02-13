// models/GeneratedContent.js
const mongoose = require('mongoose');

const GeneratedContentSchema = new mongoose.Schema({
    userId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true
    },
    type: {
        type: String,
        enum: ['image', 'video','story'],
        required: true
    },
    prompt: {
        type: String,
        required: true
    },
    shortTitle: {
        type: String,
        default: null
    },
    filePath: {
        type: String,
        required: false
    },
    thumbnailPath: { 
        type: String
    },
    status: {
        type: String,
        enum: ['pending', 'completed', 'failed'],
        default: 'pending'
    },
    createdAt: {
        type: Date,
        default: Date.now
    }
});

module.exports = mongoose.model('GeneratedContent', GeneratedContentSchema);