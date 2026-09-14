A linked list is one of the first data structures many programmers learn after arrays, and it solves a problem that arrays cannot handle gracefully: growing or shrinking without wasting memory.

Instead of storing its elements in one continuous block, a linked list is built from small units called nodes. Each node holds two things: a piece of data and a pointer to the next node in the sequence. The list only needs to remember where the first node, called the head, lives, since every other node can be reached by following the pointers one after another. The final node's pointer is set to null, which signals the end of the list.

Because nodes do not need to sit next to each other in memory, items can be inserted or removed by simply changing a pointer or two, and none of the other elements need to move. This is what makes linked lists so useful for data that changes size often. The trade-off is that reaching a specific node, say the tenth one, means walking through the nine nodes before it, since there is no way to jump straight to it the way an array allows.

A few common variations build on this same idea. A singly linked list only points forward, a doubly linked list points both forward and backward, and a circular linked list loops the last node back to the first instead of ending at null.

For a beginner, the core idea is worth holding onto: a linked list is a chain of nodes, each one pointing to the next, trading fast random access for fast, flexible insertion and removal.