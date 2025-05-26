# Job and Task Complexity Atlas

This interactive website visualizes job and task complexity metrics across occupations and geographic regions, based on BLS and O*NET data.

## Deployment Instructions

### GitHub Pages Deployment

To deploy this website to GitHub Pages:

1. Create a new GitHub repository
2. Upload all files from the `website` directory to the repository
3. Go to the repository settings
4. Scroll down to the "GitHub Pages" section
5. Select the branch you want to deploy (usually `main`)
6. Click "Save"
7. Your site will be published at `https://[your-username].github.io/[repository-name]/`

### Alternative Deployment Options

#### Netlify

1. Sign up for a free Netlify account at https://www.netlify.com/
2. Drag and drop the `website` folder onto the Netlify dashboard
3. Your site will be deployed with a random URL
4. You can configure a custom domain in the Netlify settings

#### Vercel

1. Sign up for a free Vercel account at https://vercel.com/
2. Install the Vercel CLI: `npm i -g vercel`
3. Navigate to the `website` directory
4. Run `vercel` and follow the prompts
5. Your site will be deployed to a Vercel URL

## Website Structure

- `index.html`: Main entry point for the website
- `visualizations/`: Contains all interactive visualization HTML files
- `data/`: Contains all data files used by the visualizations

## Data Sources

- Bureau of Labor Statistics (BLS) Occupational Employment and Wage Statistics
- O*NET Database (tasks, skills, and abilities)
- Standard Occupational Classification (SOC) system

## Customization

You can customize the website by:

1. Editing the `index.html` file to change text, layout, or styling
2. Updating the data files in the `data/` directory with new information
3. Modifying the visualization files in the `visualizations/` directory

## License

This project is provided for educational and research purposes.
