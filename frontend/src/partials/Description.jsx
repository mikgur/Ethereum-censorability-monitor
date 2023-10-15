import React from 'react';

function Description() {
    return (
        <div className="w-full bg-gray-900 text-white border-t border-gray-700 p-4 md:p-6 flex flex-col items-center space-y-4">
            <div className="text-center w-full md:w-auto max-w-xl">
                <p>Here is a <a href="https://www.kaggle.com/datasets/mgurevich/ethereum-transactions-with-first-seen-timestamp" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-500 underline">dataset of Ethereum transactions</a> that includes compliance statuses, validators (all the information we could gather), and the timestamp of when they were first seen in the mempool.</p>
                <p>We obtained historical mempool data from the <a href="https://docs.blocknative.com/mempool-data-program" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-500 underline">Blocknative Mempool Data Program</a>. Kudos to them!</p>
                <p>Explore our code! Check out our <a href="https://github.com/mikgur/Ethereum-censorability-monitor" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-500 underline">GitHub Repository</a>.</p>
            </div>
        </div>
    );
}

export default Description;
