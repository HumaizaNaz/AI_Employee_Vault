require('path');
require('dotenv').config(); // Load environment variables from current directory first
require('dotenv').config({ path: '../../../.env' }); // Then load from project root
const express = require('express');
const nodemailer = require('nodemailer');
const rateLimit = require('express-rate-limit');

const app = express();
// Use the exact expected value to ensure consistency
const VALID_API_KEY = "AIEMCP_RANDOM_KEY_v27RzD0xW4jL9yP7cFqA8sH3nB5gK6tE";
// Rate limiting - apply to all routes except health check
const limiter = rateLimit({
  windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 60000, // 1 minute
  max: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS) || 5, // Limit each IP to 5 requests per windowMs
  message: { error: 'Too many requests, please try again later.' },
  skip: (req, res) => req.path === '/health' // Don't rate limit health checks
});

app.use(limiter);

app.use(express.json());

// Validate API Key middleware
const validateApiKey = (req, res, next) => {
  console.log('All headers:', req.headers); // Debug log to see all headers
  const apiKey = req.headers['x-api-key'] || req.headers['X-API-Key'] || req.headers['X-Api-Key']; // Handle different cases
  // Use the hardcoded constant to ensure consistency
  const validApiKey = VALID_API_KEY;
  console.log('Received API Key:', apiKey); // Debug log
  console.log('Expected API Key:', validApiKey); // Debug log
  console.log('Environment API Key:', process.env.API_KEY); // Debug log
  if (!apiKey || apiKey !== validApiKey) {
    return res.status(401).json({ error: 'Unauthorized: Invalid API key' });
  }
  next();
};

// Use environment variables for email configuration
const transporter = nodemailer.createTransport({
  service: process.env.EMAIL_SERVICE || 'gmail',
  auth: {
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_PASS
  }
});

// Apply API key validation middleware to email endpoint
app.post('/send-email', validateApiKey, (req, res) => {
  const { to, subject, text } = req.body;

  // Input validation
  if (!to || !subject || !text) {
    return res.status(400).json({ error: 'Missing required fields: to, subject, text' });
  }

  // Sanitize inputs (basic validation)
  if (typeof to !== 'string' || typeof subject !== 'string' || typeof text !== 'string') {
    return res.status(400).json({ error: 'Invalid input types' });
  }

  const mailOptions = {
    from: process.env.EMAIL_USER,
    to,
    subject,
    text
  };

  transporter.sendMail(mailOptions, (error, info) => {
    if (error) {
      console.error('Email sending error:', error);
      res.status(500).json({ error: 'Failed to send email' });
    } else {
      console.log('Email sent successfully:', info.messageId);
      res.json({ success: true, message: 'Email sent', messageId: info.messageId });
    }
  });
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

const PORT = 3005;
app.listen(PORT, () => console.log(`MCP Email Server running securely on port ${PORT}`));