import React from 'react';
import { FaTelegram, FaTwitter, FaLinkedin} from 'react-icons/fa';

const PersonCard = ({ name, photoUrl, telegramLink = '#', twitterLink = '#', linkedinLink = '#' }) => {
  return (
    <div className="">
    <div className="bg-white shadow-lg rounded-lg overflow-hidden m-4 w-64 dark:bg-gray-800">
      <img className="w-full h-48 object-cover" src={photoUrl} alt={name} />
      <div className="p-4 bg-blue-200">
        <h2 className="text-xl font-bold mb-2 text-gray-800 dark:text-white">{name}</h2>
        <div className="flex flex-col">
          {telegramLink !== '#' && (
            <a href={telegramLink} className="flex items-center mr-2 text-gray-800 dark:text-white">
              <FaTelegram size={24} className="mr-2" />
              <span>Telegram</span>
            </a>
          )}
          {twitterLink !== '#' && (
            <a href={twitterLink} className="flex items-center mr-2 text-gray-800 dark:text-white">
              <FaTwitter size={24} className="mr-2" />
              <span>Twitter</span>
            </a>
          )}
          {linkedinLink !== '#' && (
            <a href={linkedinLink} className="flex items-center text-gray-800 dark:text-white">
              <FaLinkedin size={24} className="mr-2" />
              <span>LinkedIn</span>
            </a>
          )}
        </div>
      </div>
    </div>
    </div>
  );
};


const PersonCardList = () => {
  const people = [
    {
      name: 'Mikhail Gurevich',
      photoUrl: 'https://i.ibb.co/JxqLf95/image.jpg/400x400',
      telegramLink: 'https://t.me/gurev',
      twitterLink: 'https://twitter.com/gurevich_m',
      linkedinLink: 'https://www.linkedin.com/in/gurevichmikhail/'
    },
    {
      name: 'Petr Korchagin',
      photoUrl: 'https://i.ibb.co/QYgDFHv/image.jpg/400x400',
      telegramLink: 'https://t.me/petrovitch_sharp',
      linkedinLink: 'https://www.linkedin.com/in/petr-korchagin-194909249/'
    },
    {
      name: 'Evgeny Bezmen',
      photoUrl: 'https://i.ibb.co/Bq0zVBt/image.jpg/400x400',
      telegramLink: 'https://t.me/flashlight101',
      linkedinLink: 'https://www.linkedin.com/in/evgeny-bezmen-a89714191/'
    },
    {
      name: 'Anatoly Krestenko',
      photoUrl: 'https://i.ibb.co/z2FXZhY/image.jpg/400x400',
      telegramLink: 'https://t.me/likeblood',
      linkedinLink: 'https://www.linkedin.com/in/anatoly-krestenko-463664224/'
    }
  ];

  return (
    <div>
      <div className="flex flex-wrap justify-center text-center">
        <h1 className="text-4xl pt-24 font-bold text-transparent bg-gradient-to-r from-blue-500 to-red-500 bg-clip-text mb-8">
        Neutrality Watch team
        </h1>
      </div>
      <div className="flex flex-wrap justify-center">
      {people.map((person, index) => (
        <PersonCard key={index} {...person} />
      ))}
    </div>
    </div>

  );
};

export default PersonCardList;

