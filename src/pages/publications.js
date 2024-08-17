import React, { useEffect, useState } from 'react';
import data from '../data/data.json';
import '../styles/publications.css';

function Publications() {
    const [publications, setPublications] = useState([]);

    useEffect(() => {
        setPublications(data.publications);
    }, []);

    return (
        <div className="page-container animate-fade-in">
            <h1 className="page-title">Publications</h1>
            {publications.map((pub, index) => (
                <div key={index} className="card">
                    <h2 className="card-title">
                        <a href={pub.publisherUrl} target="_blank" rel="noopener noreferrer">
                            {pub.title}
                        </a>
                    </h2>
                    <p className="publication-publisher">
                        <strong>Published in:</strong> {pub.publisher}
                    </p>
                    <p className="publication-date">
                        <strong>Published on:</strong> {pub.publishedDate}
                    </p>
                    {pub.citations > 0 && (
                        <p className="publication-citations">
                            <strong>Citations:</strong> {pub.citations}
                        </p>
                    )}
                    {pub.doi && (
                        <p className="publication-doi">
                            <strong>DOI:</strong> <a href={pub.doi} target="_blank" rel="noopener noreferrer">{pub.doi}</a>
                        </p>
                    )}
                    {pub.abstract && (
                        <p className="publication-abstract">
                            <strong>Abstract:</strong> {pub.abstract}
                        </p>
                    )}
                </div>
            ))}
        </div>
    );
}


export default Publications;