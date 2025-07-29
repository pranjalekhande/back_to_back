import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import 'dotenv/config';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = 3000;

// Serve static files from project root
app.use(express.static(path.join(__dirname, '..')));

// API endpoint to get DeepGram API key
app.get('/api/config', (req, res) => {
    res.json({
        deepgramApiKey: process.env.DEEPGRAM_API_KEY || ''
    });
});

// Serve test page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'simple-test.html'));
});

app.get('/test', (req, res) => {
    res.sendFile(path.join(__dirname, 'simple-test.html'));
});

app.listen(PORT, () => {
    console.log(`🚀 Test server running at http://localhost:${PORT}`);
    console.log(`📝 Test page: http://localhost:${PORT}/test`);
    console.log('');
    console.log('Instructions:');
    console.log('1. Get your DeepGram API key from https://console.deepgram.com/');
    console.log('2. Open the test page in your browser');
    console.log('3. Enter your API key and click "Start Listening"');
    console.log('4. Speak into your microphone to test transcription');
});
