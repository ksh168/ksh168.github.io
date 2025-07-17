# Portfolio Website

This is a personal portfolio website built using React and NodeJS 20.19.4.

## Features

- Responsive design
- Dynamic content loading from JSON data
- Smooth scrolling and navigation
- Interactive project demos
- Contact form integration

## Technologies Used

- NodeJS
- React
- CSS3
- HTML5
- JavaScript (ES6+)

## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/ksh168/ksh168.github.io
   ```

2. Navigate to the project directory:
   ```
   cd ksh168.github.io
   ```

3. Install dependencies:
   ```
   npm install
   ```

4. Start the development server:
   ```
   npm start
   ```

5. Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

## Deployment

This site is configured to deploy to GitHub Pages. To deploy:

1. Update the `homepage` field in `package.json` with your GitHub Pages URL.

2. Run the following command:
   ```
   npm run deploy
   ```

## Project Structure

- `src/`: Contains all the source code
  - `components/`: React components
  - `pages/`: Individual page components
  - `styles/`: CSS files
  - `data/`: JSON data files
  - `utils/`: Utility functions
  - `config/`: Configuration files
- `public/`: Contains resources
  - `index.html`: Main HTML file
  - `favicon.ico`: Favicon file
  - `demoVideos/`: Demo videos
  - `404.html`: 404 page
- `package.json`: Project configuration and dependencies
- `README.md`: This file

## Resources
- [Deployment to github pages](https://create-react-app.dev/docs/deployment/#github-pages)
- [SPA GitHub Pages](https://github.com/rafgraph/spa-github-pages) - GitHub Pages doesn’t support routers that use the HTML5 pushState history API
  - [404.html](https://github.com/rafgraph/spa-github-pages/blob/gh-pages/404.html)
  - [index.html](https://github.com/rafgraph/spa-github-pages/blob/gh-pages/index.html#L21-L42)