#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2014 Luke Thomas Mergner <lmergner@gmail.com>
#
# Distributed under terms of the MIT license.

"""

"""

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base

__all__ = ('Editor', 'Task', 'Project')

class Editor(Base):
    pass

class Task(Base):
    pass

class Project(Base):
    pass
