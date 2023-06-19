import React from 'react';

import Header from '../partials/Header';
import PersonCardList from '../partials/PersonCardList';

function Team() {
  return (
    <div className="flex flex-col min-h-screen overflow-hidden">
      {/*  Site header */}
      <Header />

      {/*  Page content */}
      <main className="grow">
        <PersonCardList />
      </main>
    </div>
  );
}

export default Team;