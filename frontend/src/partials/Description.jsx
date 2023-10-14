import React from 'react';
import { FaGithub, FaKaggle } from 'react-icons/fa';

const KAGGLE_DESCRIPTION = "Data";

function Description() {
    return (
        <div className="w-full bg-gray-900 text-white border-t border-gray-700 p-4 md:p-6 flex flex-col items-center space-y-4">
            <div className="flex flex-col md:flex-row space-y-4 md:space-y-0 md:space-x-4">
                <a 
                    href="https://github.com/mikgur/Ethereum-censorability-monitor" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="bg-blue-500 text-white hover:bg-blue-600 transition duration-150 ease-in-out px-4 py-2 flex items-center space-x-2 rounded"
                >
                    <FaGithub className="w-6 h-6" />
                    <span>Repository</span>
                </a>
                <a 
                    href="https://www.kaggle.com/your-dataset-link" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="bg-blue-500 text-white hover:bg-blue-600 transition duration-150 ease-in-out px-4 py-2 flex items-center space-x-2 rounded"
                >
                    <FaKaggle className="w-4 h-4" />
                    <span>Data</span>
                </a>
            </div>
            <div className="text-center w-full md:w-auto">
                {KAGGLE_DESCRIPTION}
            </div>
        </div>
    );
}

export default Description;
