# Protocaas - Neuroscience Analysis Web App

Protocaas is a prototype web application designed for scientists in research labs who want to efficiently manage and conduct neurophysiology data analysis. Whether you are working with your own data or utilizing resources from the [DANDI Archive](https://dandiarchive.org/), Protocaas provides a user-friendly platform for organizing, running, and sharing neuroscientific processing jobs.

:warning: **Please note:** This software is currently in the prototype phase and is not recommended for production use.

* [Access the live site](https://protocaas.vercel.app)
* [Learn how to host a compute resource](./doc/host_compute_resource.md)

## System Requirements

To use Protocaas, you only need a web browser. No additional software installation is required. Simply open your preferred web browser and navigate to the [live site](https://protocaas.vercel.app) to get started.

If you want to [host your own compute resource](./doc/host_compute_resource.md) for processing, you will need a Linux machine with optional access to a Slurm cluster or AWS resources.

## Workspaces and Projects

Protocaas organizes datasets into workspaces and projects, streamlining your data management process. Each workspace is associated with an owner and can include optional collaborators. You can choose to make your workspaces public or private, and they can be listed or unlisted. Within your workspaces, you can create projects, which consist of files and processing jobs.

In each project, files serve as either pointers to external data sources (e.g., DANDI assets) or as the output of specific processing jobs. These files are typically formatted in NWB (Neurodata Without Borders) format. To get started, you can use the DANDI import tool to seamlessly import data from DANDI repositories. Once imported, you can define processing jobs that take these raw data files as input and generate new project files as output. Project files are immutable, and each file is assigned a unique URL, size, and associated metadata.

## Processing Apps

Protocaas processing tools are organized into plugin apps which are containerized executable programs. At this point, there are only [a couple processing apps available](https://github.com/scratchrealm/pc-spike-sorting):

- Spike sorting using Kilosort 3
- Spike sorting using MountainSort 5

As the project matures, we will add more apps to this list. Users can also contribute their own processing apps.

### LICENSE

Apache 2.0

### Authors

Jeremy Magland, Center for Computational Mathematics, Flatiron Institute

Ben Dichter and Luiz Tauffer, CatalystNeuro