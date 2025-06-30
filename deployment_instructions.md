# Deployment Instructions for Job and Task Complexity Atlas

This document provides instructions for deploying the Job and Task Complexity Atlas website to GitHub Pages or other hosting platforms.

## GitHub Pages Deployment

GitHub Pages is a free hosting service that allows you to publish your website directly from a GitHub repository. Follow these steps to deploy your website:

1. **Create a GitHub Repository**
   - Sign in to your GitHub account
   - Click the "+" icon in the top right corner and select "New repository"
   - Name your repository (e.g., "job-complexity-atlas")
   - Make the repository public
   - Click "Create repository"

2. **Upload the Website Files**
   - Extract the `website_updated.zip` file to your local computer
   - In your new GitHub repository, click "uploading an existing file"
   - Drag and drop all the files from the extracted website folder
   - Commit the changes with a message like "Initial website upload"

3. **Enable GitHub Pages**
   - Go to your repository's "Settings" tab
   - Scroll down to the "GitHub Pages" section
   - Under "Source", select "main" branch and "/" (root) folder
   - Click "Save"
   - GitHub will provide you with a URL where your site is published (typically https://yourusername.github.io/job-complexity-atlas/)

4. **Verify Deployment**
   - Wait a few minutes for GitHub to build and deploy your site
   - Visit the provided URL to ensure everything is working correctly
   - Test all visualizations and navigation

## Alternative Deployment Options

### Netlify

1. Sign up for a free Netlify account at https://www.netlify.com/
2. Drag and drop your website folder to the Netlify dashboard
3. Netlify will automatically deploy your site and provide a URL

### Vercel

1. Sign up for a free Vercel account at https://vercel.com/
2. Install the Vercel CLI: `npm i -g vercel`
3. Navigate to your website directory in the terminal
4. Run `vercel` and follow the prompts
5. Vercel will deploy your site and provide a URL

## Custom Domain Setup

If you want to use a custom domain (e.g., jobcomplexityatlas.com):

1. Purchase a domain from a domain registrar (e.g., Namecheap, GoDaddy)
2. Follow the instructions for your chosen hosting platform to configure the custom domain
   - For GitHub Pages: In repository settings, add your custom domain in the "GitHub Pages" section
   - For Netlify/Vercel: Add your custom domain in the site settings

3. Update your domain's DNS settings to point to your hosting provider
   - For GitHub Pages: Create A records pointing to GitHub's IP addresses
   - For Netlify/Vercel: Create a CNAME record pointing to your provided subdomain

## Updating Your Website

To update your website after making changes:

1. Make your changes to the local files
2. Upload the modified files to your repository or hosting platform
3. The changes will automatically be deployed

## Troubleshooting

If you encounter issues with your deployment:

- Ensure all file paths are relative, not absolute
- Check that all required files are included in the upload
- Verify that the index.html file is in the root directory
- For visualization issues, check the browser console for JavaScript errors

For additional help, refer to the documentation of your chosen hosting platform.
