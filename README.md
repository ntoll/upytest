[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=816765904)

# 🐍📜 PyScript with GitHub Codespaces and Copilot

_Create, customize and deploy your own [PyScript](https://pyscript.net)
website in minutes._ ✨

In this template repository we have the development environment and base set
and ready to go. So that you can immediately launch your
[Codespace](https://github.com/features/codespaces/) environment and start
customizing your site using [Copilot](https://copilot.github.com) to help you
write code faster.

* **Who is this for?** __Anyone__ looking to create a
  [PyScript](https://pyscript.net/) site, learn web development, or test out
  Codespaces.
* **How much experience do you need?** __Zero__. You decide how much you want
  to customize based on your experience, and time available.
* **Tools needed:** _None_. No need to install anything! All you need is a web
  browser.
* **Prerequisites:** _None_. This template includes your development
  environment and deployable web app for you to create your own site.

## About this PyScript template

This template includes the minimal viable PyScript application, from which you
can build.

### Quick Start

1. Click the **Use this Template** button and then **Create a new repository** as can be seen in the image below.
   Note: Make sure you've signed in to GitHub otherwise, you wouldn't see the **Use this Template** button.
![PyScript web application](https://raw.githubusercontent.com/education/codespaces-project-template-js/main/__images__/use-this-template.png "Use this Template Image Guide")
1. Select the repository owner (e.g. your GitHub account)
1. Enter a unique name for your new repository
1. Click the **Code** button
1. Click **Create Codespace on main** button
1. Customize your PyScript site with Copilot
1. [Deploy your site](#-deploy-your-web-application)

<details>
   <summary><b>🎥 To learn more about Codespaces, watch our video tutorial series</b></summary>

   [![Codespaces Tutorial](https://img.youtube.com/vi/ozuDPmcC1io/0.jpg)](https://aka.ms/CodespacesVideoTutorial "Codespaces Tutorial")
</details>

## 🗃️ PyScript template

This repo is a GitHub template to build a PyScript web application. The goal is
to give you a template that you can immediately utilize to create your own
PyScript website through Codespaces.

The repo contains the following:

* `.devcontainer/devcontainer.json`: Configuration file used by Codespaces to
  configure Visual Studio Code settings, such as the enabling of additional
  extensions.
* `config.json`: the
  [PyScript configuration](https://docs.pyscript.net/2024.6.1/user-guide/configuration/)
  used by your application.
* `index.html`: the
  [HTML page](https://docs.pyscript.net/2024.6.1/user-guide/first-steps/)
  used to load your PyScript application.
* `main.py`: the [Python script](https://pyscript.net/) to run.
* `mini-coi.js`: a
  [utility](https://docs.pyscript.net/2024.6.1/user-guide/workers/#http-headers)
  to ensure all PyScript's features are available.
* `README.md`: this file (that you're reading right now).

## 🚀 Getting started

This PyScript project contains everything you need so that you can immediately
open Codespaces, see it running, and deploy at any point.

Your development environment is all set for you to start.

* Visual Studio Code with the [Python plugin](https://code.visualstudio.com/docs/languages/python) enabled.
* The [LiveServer](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer) plugin (so you can view your site).
* GitHub [copilot support](https://github.com/features/copilot) (if you have it enabled for your account).

### Create your PyScript app 

1. Create a repository from this template. Use this
   [create repo link](https://github.com/ntoll/codespaces-project-template-pyscript/generate).
   Select the repository owner, provide a name, a description if you'd like and
   if you'd like the new repository to be public or private.
1. Before creating the Codespace, enable GitHub Copilot for your account.
1. Navigate to the main page of the newly created repository.
3. Under the repository name, use the Code drop-down menu, and in the
   Codespaces tab, select "Create codespace on main".
4. Wait as GitHub initializes the Codespace.
5. When complete you will see your Codespace load with a terminal section at
   the bottom. Codespaces will install all the required extensions in your
   container. Once the package installs are completed, you'll be able to start
   editing and start a LiveServer to see your site.

## 🏃 Deploy your web application

Project includes the setup needed for you to deploy **FREE** to either
[Azure Static Web Apps](https://azure.microsoft.com/products/app-service/static/?WT.mc_id=academic-79839-sagibbon)
_**or**_ [GitHub Pages](https://pages.github.com/)</a>. Instructions are
included below for Azure. The following YouTube video demonstrates how to get
your Codespace up and running, then deployed to GitHub Pages in under two 
minutes:

[![PyScript to Github pages in 2 minutes.](https://img.youtube.com/vi/dmIWFcJ2UTI/0.jpg)](https://www.youtube.com/watch?v=dmIWFcJ2UTI)

### Azure Static Web Apps

[Azure Static Web Apps](https://azure.microsoft.com/products/app-service/static/?WT.mc_id=academic-79839-sagibbon)
is Microsoft's hosting solution for static sites (or sites that are rendered in
the user's browser, not on a server) through Azure. This service provides
additional opportunities to expand your site through Azure Functions,
authentication, staging versions and more.

You'll need both Azure and GitHub accounts to deploy your web application. If
you don't yet have an Azure account you can create it from within during the
deploy process, or from below links:

* [Create a (no Credit Card required) Azure For Students account](https://azure.microsoft.com/free/students/?WT.mc_id=academic-79839-sagibbon)
* [Create a new Azure account](https://azure.microsoft.com/?WT.mc_id=academic-79839-sagibbon)

With your project open in Codespaces:

1. Click Azure icon in the left sidebar. Log in if you are not already, and if
   new to Azure, follow the prompts to create your account.
1. From Azure menu click “+” sign and then “Create Static Web App”.
1. If you are not logged into GitHub you will be prompted to log in. If you
   have any pending file changes you will then be prompted to commit those
   changes.
1. Set your application information when prompted:
    1. **Region**: pick the one closest to you
    1. **Project structure**: select "React"
    1. **Location of application code**: `/`
    1. **Build location**: `dist`
1. When complete you will see a notification at the bottom of your screen, and
   a new GitHub Action workflow will be added to your project. If you click
   “Open Action in GitHub” you will see the action that was created for you,
   and it is currently running.
![Azure Static Web App deploy](https://github.com/education/codespaces-project-template-js/raw/main/__images__/swa-deploy.gif "Azure Static Web App deploy")
1. To view the status of your deployment, find your Static Web App resource in
   the Azure tab in the VS Code left side bar.
1. Once deployment is complete, you can view your brand new new publicly
   accessible application by right clicking on your Static Web App resource and
   selecting "Browse Site".

> **Issues?** When creating your Static Web app, if you are prompted to select
> an Azure subscription and are not able to select a subscription, check the
> "Accounts" tab in VS Code. Make sure to choose the "Grant access to ..."
> options if those options appear. Should you receive the error-message
> "RepositoryToken is invalid. ..." switch to Visual Studio Code for the Web
> (vscode.dev) and repeat the steps there.

> 🤩 **Bonus**: [Setup a custom domain for your Azure Static Web App](https://learn.microsoft.com/en-us/shows/azure-tips-and-tricks-static-web-apps/how-to-set-up-a-custom-domain-name-in-azure-static-web-apps-10-of-16--azure-tips-and-tricks-static-w/?WT.mc_id=academic-79839-sagibbon)

## 🔎 Found an issue or have an idea for improvement?
Help us make this template repository better by [letting us know and opening an issue!](/../../issues/new).
