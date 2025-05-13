// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract GameToken is ERC20 {
    constructor() ERC20("Game Token", "GAME") {
        // Mint initial supply to contract deployer
        _mint(msg.sender, 1000000 * 10 ** decimals());
    }
    
    // Function to mint new tokens (only for testing)
    function mint(address to, uint256 amount) public {
        _mint(to, amount);
    }
} 