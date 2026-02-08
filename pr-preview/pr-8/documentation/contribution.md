# Contribution Guide

This document provides guidelines for contributing to the Job and Task Complexity Atlas project. We welcome contributions that improve the data processing, enhance visualizations, extend the analysis to new regions or time periods, or refine the theoretical framework.

## Ways to Contribute

There are several ways you can contribute to this project:

1. **Data Processing Improvements**: Enhance the scripts that process BLS and O*NET data
2. **Visualization Enhancements**: Improve existing visualizations or create new ones
3. **Theoretical Refinements**: Suggest improvements to the complexity calculation methodology
4. **Geographic Extensions**: Add support for new countries or regions
5. **Documentation**: Improve the documentation or add tutorials
6. **Bug Fixes**: Fix issues in the existing codebase

## Getting Started

1. **Fork the repository**: Create your own copy of the project
2. **Clone your fork**: Download your fork to your local machine
3. **Create a branch**: Make a new branch for your contribution
4. **Make your changes**: Implement your improvements
5. **Test your changes**: Ensure your changes work as expected
6. **Submit a pull request**: Share your changes with the project maintainers

## Code Style Guidelines

Please follow these guidelines when contributing code:

- Use clear, descriptive variable and function names
- Include comments explaining complex logic
- Write docstrings for all functions and classes
- Follow PEP 8 style guidelines for Python code
- Keep functions focused on a single task
- Include error handling for robust operation

## Documentation Guidelines

When contributing documentation:

- Use clear, concise language
- Include step-by-step instructions where appropriate
- Provide examples to illustrate concepts
- Link to relevant external resources
- Use proper Markdown formatting

## Testing

Before submitting your contribution:

- Test your changes with different datasets
- Verify that visualizations render correctly
- Check that calculations produce expected results
- Ensure compatibility with the existing codebase

## Submitting Changes

When submitting a pull request:

1. Describe the purpose of your changes
2. Explain how your changes improve the project
3. List any dependencies your changes introduce
4. Mention any issues your changes address
5. Include screenshots for visualization changes

## Adding Support for New Countries

To add support for a new country:

1. Create a new data processing script in `scripts/data_processing/`
2. Implement the necessary transformations to convert country-specific data to the project's format
3. Document the data sources and any special considerations
4. Test the integration with the complexity calculation and visualization scripts
5. Add examples to the documentation

## Extending the Time Series

To extend the analysis to new time periods:

1. Process the new time period data using the existing scripts
2. Ensure consistent methodology across time periods
3. Create visualizations that highlight changes over time
4. Document any methodological adjustments needed for different time periods

## Questions and Support

If you have questions about contributing, please open an issue in the repository or contact the project maintainers.

Thank you for your interest in improving the Job and Task Complexity Atlas!
