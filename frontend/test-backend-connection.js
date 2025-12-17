// Test if backend is accessible
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function testBackend() {
  try {
    const response = await fetch(`${API_URL}/api/v1/projects`);
    const data = await response.json();
    console.log('✅ Backend is accessible!');
    console.log('Status:', response.status);
    console.log('Projects:', data);
  } catch (error) {
    console.log('❌ Cannot connect to backend:', error.message);
  }
}

testBackend();
