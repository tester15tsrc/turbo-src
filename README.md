<p align="left">
  <a href="https://turbosrc.org#gh-light-mode-only">
    <img src="images/turbosrc-light-big.png" width="500px" alt="TurboSrc logo"/>
  </a>
  <a href="https://turbosrc.org#gh-dark-mode-only">
    <img src="images/turbosrc-dark-big.png" width="500px" alt="TurboSrc logo"/>
  </a>
</p>
<p align="left">
  <em><strong>Empowering open source communities</em></strong>
</p>

<br>

TurboSrc is a unique platform designed to promote transparency and boost community participation in your open-source projects. Our innovative voting system for pull requests not only empowers contributors but also enriches the overall development experience.

It currently works as a Chrome web extension for Github, but the plan is to develop it across multiple code hosts if necessary. The Turbosrc instance has a full api and its own internal representation of code bases and their pull requests.

While we're currently in active development and the pre-alpha phase, your support and patience are much appreciated. Our goal is to develop TurboSrc into a valuable tool for all open-source projects.

For your convenience, we make it super easy to experiment with TurboSrc in the meantime. Setup a local instance and safely play around as much as you like: skip to [Setting up a local TurboSrc instance](#setting-up-a-local-turbosrc-instance).

## Highlights
* **Launch Your Own TurboSrc Instance:** Enhance your project's community involvement by setting up your unique TurboSrc instance.
* **Harness VotePower:** Empower your TurboSrc instance users with the ability to vote on pull requests using VotePower.
* **Effortless VotePower Distribution:** Distribute VotePower to your project's community members directly through your Github page integrated with TurboSrc.

Let's get you started!

## Understanding VotePower
In your TurboSrc instance, each user has the capacity to vote on pull requests, courtesy of VotePower. Essentially, each VotePower translates to a single vote that can be cast for or against pull requests. Although a user may possess multiple VotePowers (e.g., 100,000 VotePower), the total supply is capped at one million per project within your TurboSrc instance. So, if a user holds 100,000 VotePower, they have 100,000 votes at their disposal.

Note: VotePower is specific to each project. Consequently, if you hold VotePower in one project, it cannot be used in another.

![ezgif com-video-to-gif](https://github.com/turbo-src/turbo-src/assets/75996017/3e86e207-a1d4-4d84-9f8c-0b85be123fc1)

## Distributing VotePower
As a project maintainer, you can distribute VotePower to the community members of the project hosted on your TurboSrc instance. Simply look up users via the web extension on your Github page linked with TurboSrc, and transfer VotePower to them. Users can sign up conveniently via the web extension.

We encourage project maintainers to distribute VotePower to their contributors and sponsors, recognizing and rewarding their merit.

Bear in mind, the supply of VotePower is created by the initial maintainer for each project independently within your TurboSrc instance. Hence, the distribution of VotePower might differ across various projects.

![ezgif com-video-to-gif (2)](https://github.com/turbo-src/turbo-src/assets/75996017/8a4ee3f3-c5a0-45f7-905f-962c16ade766)

## TurboSrc Usage
TurboSrc is designed for simplicity and ease of use. Users holding VotePower for a project within your TurboSrc instance can easily visit its pull request page on Github and utilize features that allow them to vote and track ongoing activities.

To add your project to your TurboSrc instance, visit your project's Github page and open the TurboSrc Extension. There you will find an option to add your project to TurboSrc. Just sign in to your Github account for authentication.

![ezgif com-crop (1)](https://github.com/turbo-src/turbo-src/assets/75996017/9b25fb92-f8e5-493b-b4d2-f6bc37cf49f7)

## Setting up a local TurboSrc instance

Setting up your own local TurboSrc instance is straightforward. Please note that the online hosting setup instructions are not yet available.

To assist you, we've provided a step-by-step guide to help you get started with your local instance. To simplify the process, the company Reibase conveniently hosts a Github Oauth for your local instance, saving you the hassle. If you prefer to handle this yourself, you can find the necessary code [here](https://github.com/turbo-src/turbosrc-auth).

Remember, your local instance is exclusive to you. No one else will be able to interact with it, so feel free to explore and experiment without any concerns!

**1. Install dependencies**

Install

- docker
- docker-compose
- yarn

**2. Installation**

To begin, clone this project.

```
git clone --recurse-submodules https://github.com/turbo-src/turbo-src.git
```

**3. Configure Turbosrc Service**

You'll need a `turbosrc.config` file in the root directory.

```
{
    "GithubName": "myGithubName",
    "GithubApiToken": "myGithubApiToken",
    "Secret": "mySecret",
    "TurboSrcID": ""
}
```

Optionally, you can add a TurboSrcID. Long story, leave it blank for now; It enables a future feature not fully rolled-out.

##### a. Get your Github API Token

[See here.](https://docs.github.com/en/enterprise-server@3.4/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)

You'll need the following scopes checked off:

- repo (all repo scopes)

If you want ci/cd automatically configured for you (run end-to-end tests or want to contribute to Turbosrc development), you'll also need these scopes:

- delete repo
- workflow

##### b. Generate a secret

It can be anything, as long as no one can guess it.

##### c. Create the turbosrc.config

It should be in this form:

```
{
    "GithubName": "myGithubName",
    "GithubApiToken": "myGithubApiToken",
    "Secret": "mySecret",
    "TurboSrcID": ""
}
```

You can leave the value of `TurboSrcID` as is above, just modify the other fields.

Here is a fake turbosrc.config with pretend info:

```
{
    "GithubName": "foss4ever",
    "GithubApiToken": "ghp_bAcAXk...",
    "Secret": "mysupersafesecretknowonecanguess",
    "TurboSrcID": ""
}
```

**4. Intitialize Turbosrc**

`./tsrc-dev init`

It will configure Turbosrc for you using your turbosrc.config. You shouldn't see any output from this command.

**5. Launch Turbosrc**

```
./tsrc-dev start
```

**6. Load the Extension**

From the chrome-extension directory, install dependencies and start the local development server:

Install dependencies.

```
yarn install
```
Start the local development server for the chrome extension and build the chrome extension.

```
yarn devLocal
```
You may stop the local devopmemnt server after it finishes, but if you leave it on it will automatically rebuild the chrome extension for you if you make code changes to the chrome-extension submodule.

Then, in a Chromium based web browser:

1. Go to Manage Extensions
2. Enable developer mode
3. Select Load unpacked
4. Select the `dist` directory in `chrome-extension`. You can then open the Turbosrc web extension in your browser.

![loadextension](https://github.com/turbo-src/turbo-src/assets/75996017/ca652882-92ee-4dbd-9c55-781e8c63613a)

## Developer usage

#### Start TurboSrc

```
./tsrc-dev start
```

#### Stop TurboSrc

```
./tsrc-dev stop
```

#### Get lastest changes

`git pull` and `git submodule update --remote`

### Make changes

Here is an example

**1. Checkout feature branch in the turbo-src**

```git checkout -b myFeature```

**2. Checkout feature branch in the targeted submodule**

```
cd turbosrc-engine
git checkout -b myFeature
```

**3. Stage and commit in both the submodule and monorepo after you make changes.**

`turbosrc-engine`

```
git add <file>
git commmit -m "New feature!"
```

`turbo-src`

```
git add <submodule>
git commmit -m "New feature!"
```

**4. Push changes to both the submodule and the monorepo.**

`turbosrc-engine`

```
git push origin myFeature
```

`turbo-src`

```
git push origin myFeature
```

**5. Go back to master and forget about myFeature**

`turbo-src`

```
git checkout master
git submodule update --init --recursive
```

**6. You want to go back into myFeature branch.**

`turbo-src`

```
git checkout myFeature
git submodule update --init --recursive
```

**7. Let's say another developer wants to experiment with this new feature.**

`turbo-src`

```
git fetch myFeature
git checkout myFeature
git submodule update --remote
``

### graphiQL query examples

You may want to query the graphql endpoint in the browser for development purposes.

Locally, go to `http://localhost:4000/graphql`. If hosting a network (most likely you are not), go to your domain name or ipaddress endpoint `https://<address>` (no `graphql` appended to the address).

Create a user.

```
query {
  createUser(
    owner: "",
    repo: "",
    contributor_id: "0x09D56A39599Dd81e213EB2A9Bd6785945B662662",
    contributor_name: "tsrctester1",
    contributor_signature: "e0c911adbce919ea366cdeb5015b18b0e7980e659c3a89cd962a29ff743370b8",
    token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJnaXRodWJUb2tlbiI6ImdocF9UcmFTbFJwVDhkczJucXk0OGxEdE1oTHNieXlpNmgxenRiWWQiLCJpYXQiOjE2ODIxNzkzNDN9.IPcPO05RaEjb8fk0wd7AiiaPjWMRri5P9vMYtALnZHI"
  )
}
```

Get the name of a contributor from their contributor ID.

```
query {
  getContributorName(
    owner: "tsrctester1",
    repo: "demo",
    defaultHash: "defaultHash4",
    contributor_id: "0x09D56A39599Dd81e213EB2A9Bd6785945B662662"
  )
}
```