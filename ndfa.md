```mermaid
stateDiagram-v2
    **q_0** --> **q_0** : 0
    **q_0** --> **q_1** : 1
    start --> **q_0** : ε
    start --> **q_1** : ε
    **q_1** --> **q_1** : 1
    **q_1** --> **q_0** : 0

```