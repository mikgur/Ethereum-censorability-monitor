import React from 'react';

import Header from '../partials/Header';
import PageIllustration from '../partials/PageIllustration';
import HeroHome from '../partials/HeroHome';
import VisChart from '../partials/VisChart';
import RatioChart from '../partials/RatioChart';
import PoolChart from '../partials/PoolChart';
import LatencyChart from '../partials/LatencyChart';
import MedianChart from '../partials/MedianChart';
import Percent from '../partials/Percent';

function Home() {
  return (
    <div className="flex flex-col min-h-screen overflow-hidden">
      {/*  Site header */}
      <Header />

      {/*  Page content */}
      <main className="grow">
        <div className="relative max-w-6xl mx-auto h-0 pointer-events-none" aria-hidden="true">
          <PageIllustration />
        </div>
        <HeroHome />
        <LatencyChart />
        <div style={{height: 100, weight: 200}}></div>
        <Percent />
        <div style={{height: 100, weight: 200}}></div>
        <MedianChart />
        <div style={{height: 200, weight: 200}}></div>
        <VisChart />
        <div style={{height: 300, weight: 200}}></div>
        <RatioChart />
        <div style={{height: 300, weight: 200}}></div>
        <PoolChart />
        <div style={{height: 100, weight: 200}}></div>
        <div class="flex flex-wrap justify-center">
        <a href="https://github.com/mikgur/Ethereum-censorability-monitor">
          <img src="src/images/github.png" width="100" height="100"></img>
        </a>
        </div>
      </main>
    </div>
  );
}

export default Home;