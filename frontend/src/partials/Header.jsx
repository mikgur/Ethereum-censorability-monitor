import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { faBars } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';

function Header() {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };

  return (
    <header className="absolute w-full z-30">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-20">

          {/* Site branding */}
          <div className="shrink-0 mr-4">
            {/* Logo */}
          </div>

          {/* Navigation links */}
          <nav className="hidden md:flex md:flex-grow items-center flex justify-end flex-wrap">
            <Link to="/" className={`block text-white font-bold text-lg mr-4 hover:text-gray-400 ${location.pathname === '/' ? 'text-gray-400' : ''}`} style={{flexShrink: 0}}>
              Home
            </Link>
            <Link to="/team" className={`block text-white font-bold text-lg mr-4 hover:text-gray-400 ${location.pathname === '/team' ? 'text-gray-400' : ''}`} style={{flexShrink: 0}}>
              Team
            </Link>
          </nav>

          {/* Mobile Navigation */}
          <nav className="md:hidden block">
            <button onClick={toggleMobileMenu} className="flex items-center justify-center text-white focus:outline-none">
              <svg className="h-6 w-6 fill-current mr-2" viewBox="0 0 24 24">
                <path className={`${mobileMenuOpen ? 'hidden' : 'block'}`} d="M4 6h16M4 12h16M4 18h16"></path>
                <path className={`${mobileMenuOpen ? 'block' : 'hidden'}`} d="M6 18L18 6M6 6l12 12"></path>
              </svg>
              <FontAwesomeIcon icon={faBars} className="h-6 w-6 fill-current mr-2 mt-8" />
              
            </button>
            <div className={`mt-2 ${mobileMenuOpen ? 'block' : 'hidden'}`}>
              <Link to="/" className={`block text-white font-bold text-lg mb-2 hover:text-gray-400 ${location.pathname === '/' ? 'text-gray-400' : ''}`}>
                Home
              </Link>
              <Link to="/team" className={`block text-white font-bold text-lg mb-2 hover:text-gray-400 ${location.pathname === '/team' ? 'text-gray-400' : ''}`}>
                Team
              </Link>
            </div>
          </nav>

        </div>
      </div>
    </header>
  );
}

export default Header;

