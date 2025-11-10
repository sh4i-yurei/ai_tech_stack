# Documentation and Project Management Guide

This document outlines the standard operating procedure for documentation, project management, and versioning for projects by sh4i-yurei. Adhering to this guide ensures consistency, automates tedious tasks, and creates a structured foundation for generating public-facing content like blog posts.

## 1. Project Tracking: GitHub Issues

All tasks, bugs, feature ideas, and even potential blog post topics should be tracked as **GitHub Issues**.

- **Creation:** Create a new issue for any distinct piece of work.
- **Titling:** Give the issue a clear, descriptive title.
- **Labeling:** Use labels to categorize issues. Recommended labels include:
    - `bug`: A problem with existing code.
    - `feature`: A new feature or enhancement.
    - `documentation`: A task related to writing or updating documentation.
    - `refactor`: A code change that neither fixes a bug nor adds a feature.
    - `blog-post`: An idea or task for a new article on the website.
    - `chore`: Routine maintenance tasks.

## 2. Knowledge Base: The GitHub Wiki

The **GitHub Wiki** serves as the central, long-form knowledge base for a project. It is for persistent information, not transient tasks.

- **Purpose:** To store project architecture details, setup instructions, design decisions, and other "living" documentation.
- **Process:**
    1. Navigate to the "Wiki" tab in the GitHub repository.
    2. Create pages for different subjects (e.g., "Project Setup," "Deployment Process," "Architecture Overview").
    3. This content can be refined over time and used as a primary source for writing detailed blog posts.

## 3. Committing Changes: Conventional Commits

All Git commits **MUST** follow the [Conventional Commits specification](https://www.conventionalcommits.org/). This is critical for automating changelogs and versioning.

The commit message format is: `<type>[optional scope]: <description>`

- **Common Types:**
    - `feat`: A new feature for the user. (Triggers a MINOR version bump)
    - `fix`: A bug fix for the user. (Triggers a PATCH version bump)
    - `docs`: Changes to documentation only.
    - `style`: Formatting changes, missing semi-colons, etc.
    - `refactor`: A code change that neither fixes a bug nor adds a feature.
    - `test`: Adding missing tests or correcting existing tests.
    - `chore`: Updating build tasks, package manager configs, etc.

- **Breaking Changes:** For a change that breaks backward compatibility, add `BREAKING CHANGE:` to the commit message's footer. This triggers a MAJOR version bump.

## 4. Creating a Release: Automated Versioning & Changelog

When you have completed a set of features or fixes, you can create a new release.

- **Process:**
    1. Ensure all your changes are committed.
    2. Run the release script from your terminal:
       ```bash
       npm run release
       ```
- **What it Does:** This command reads all the `feat`, `fix`, and `BREAKING CHANGE` commits since the last tag, automatically determines the new version number (e.g., 1.0.0 -> 1.1.0), updates the `CHANGELOG.md` file, and creates a new Git tag for the release.

## 5. Publishing to GitHub

After creating a release, you need to push your changes and the new tags to GitHub.

- **Command:**
  ```bash
  git push --follow-tags origin main
  ```
  *(Replace `main` with your repository's default branch if different.)*

This makes the new version, changelog, and all associated code public and officially part of the project's history.
