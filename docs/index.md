The Smart Managed Pools service is in charge of conducting investment strategies by executing transfer operations in liquidity pools.  This functionality is fed from the output produced by the ML APY Prediction Oracle service, and is in charge of building and submitting the appropriate transactions to execute the orders. At every decision step, a number of things could occur. The service might:

* Do nothing, because the funds are currently distributed according to the optimal investment strategy published.
* Do nothing, because the fees of executing the operations would exceed the benefits.
* Execute a capital swap between liquidity pools to benefit from a more advantageous position. E.g., withdrawing from one liquidity pool and depositing into another that is more profitable, or swapping between assets.


##Run the code

!!! info
	This section will be added soon.


##Build your own

!!! info
	This section will be added soon.
