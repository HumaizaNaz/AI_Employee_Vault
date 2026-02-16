require('path');
console.log('Loading .env from current directory...');
require('dotenv').config(); // Load from current directory first

console.log('Environment variables after loading current directory:');
console.log('API_KEY from .env:', process.env.API_KEY);
console.log('EMAIL_USER from .env:', process.env.EMAIL_USER);
console.log('EMAIL_PASS from .env:', process.env.EMAIL_PASS);
console.log('Expected constant value:', "AIEMCP_RANDOM_KEY_v27RzD0xW4jL9yP7cFqA8sH3nB5gK6tE");

// Also try loading from parent directory
console.log('\nLoading .env from parent directory...');
require('dotenv').config({ path: '../../../.env' });

console.log('Environment variables after loading parent directory:');
console.log('API_KEY from .env:', process.env.API_KEY);
console.log('EMAIL_USER from .env:', process.env.EMAIL_USER);
console.log('EMAIL_PASS from .env:', process.env.EMAIL_PASS);