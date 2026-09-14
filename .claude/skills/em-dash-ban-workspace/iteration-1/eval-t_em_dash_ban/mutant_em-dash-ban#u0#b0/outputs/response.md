A linked list is one of the simplest ways to store a list of things in memory, and it works a little differently from the arrays you may already know.

Imagine a scavenger hunt. Each clue tells you what to find, and then it tells you where to go for the next clue. You do not need to know the location of every clue in advance; you just need the first one, and each clue leads you to the next until you reach the end.

That is exactly how a linked list works. Instead of storing every item together in one continuous block of memory like an array does, a linked list stores each item in its own little package called a node. Each node holds two things: the actual piece of data you care about, and a pointer (a reference) to the next node in the list. The list itself just keeps track of where the first node lives, often called the head. From there, you can follow the chain of pointers, one node at a time, until you hit the last node, which points to nothing, signaling the end of the list.

This structure gives linked lists some nice advantages. Adding or removing an item from the middle of the list is cheap, because you only need to update a couple of pointers rather than shifting every other element over, the way you would with an array. Linked lists can also grow or shrink easily, since you are not locked into a fixed block of memory decided in advance.

The trade-off is that you lose quick, random access. If you want the fifth item in an array, you can jump straight to it. In a linked list, you have to start at the head and walk through the nodes one by one until you count your way to the fifth one. There is no shortcut, because the only thing connecting the nodes is the chain of pointers.

There are a few common variations worth knowing. A singly linked list, like the one described above, only points forward to the next node. A doubly linked list adds a second pointer in each node that points backward to the previous node, making it easier to traverse in both directions. A circular linked list connects the last node back to the first, forming a loop instead of a hard stop.

At its heart, a linked list is a simple idea: a chain of nodes, each one holding some data and a pointer to the next. Once that clicks, you will start to see it as the foundation for many other data structures, including stacks, queues, and even more advanced trees and graphs.