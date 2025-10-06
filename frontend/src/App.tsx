import { useState } from 'react';

// The main component rendered in the extension popup (index.html)
function App() {
  const [companyScore, setCompanyScore] = useState(3.8);
  const [isLoading, setIsLoading] = useState(false);

  const fetchScore = () => {
    setIsLoading(true);
    // Simulate fetching the score from the future FastAPI backend
    setTimeout(() => {
      const newScore = (Math.random() * (4.5 - 3.0) + 3.0).toFixed(1);
      setCompanyScore(parseFloat(newScore));
      setIsLoading(false);
    }, 1500);
  };
  
  // Tailwind classes ensure a clean, modern look inside the small popup window
  return (
    <div className="p-4 w-[300px] h-[350px] font-sans bg-gray-50 flex flex-col space-y-4">
      <h1 className="text-xl font-bold text-indigo-700">
        Company Happiness Index
      </h1>
      
      <div className="bg-white p-4 rounded-xl shadow-lg border border-indigo-200 flex-grow">
        <p className="text-sm font-medium text-gray-500 mb-2">
          Overall Score (Simulated)
        </p>
        
        <div className="flex items-end justify-between mb-4">
          <span className="text-6xl font-extrabold text-green-600">
            {companyScore}
          </span>
          <span className="text-2xl text-gray-400">/ 5.0</span>
        </div>
        
        <p className="text-xs text-gray-500 italic">
          This data is currently static. Next step is to connect to FastAPI.
        </p>
        
        <div className="mt-4">
          <h2 className="text-md font-semibold text-gray-700 mb-2">Key Factors</h2>
          <ul className="text-sm space-y-1">
            <li className="flex justify-between items-center text-gray-600">
              Work-Life Balance: <span className="font-semibold text-indigo-500">4.1</span>
            </li>
            <li className="flex justify-between items-center text-gray-600">
              Culture & Ethics: <span className="font-semibold text-indigo-500">3.5</span>
            </li>
            <li className="flex justify-between items-center text-gray-600">
              Salary & Growth: <span className="font-semibold text-indigo-500">3.8</span>
            </li>
          </ul>
        </div>
      </div>
      
      <button
        onClick={fetchScore}
        disabled={isLoading}
        className={`w-full py-2 rounded-lg text-white font-semibold transition duration-150 ${
          isLoading
            ? 'bg-indigo-300 cursor-not-allowed'
            : 'bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 shadow-md hover:shadow-lg'
        }`}
      >
        {isLoading ? 'Loading Score...' : 'Refresh Score'}
      </button>
      
    </div>
  );
}

export default App;
