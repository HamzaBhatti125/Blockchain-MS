pragma solidity ^0.8.28;

contract FareAdjustment {
    address public owner;
    uint256 public fare;
    uint256 public occupancy;

    constructor(uint256 initialFare) {
        owner = msg.sender;
        fare = initialFare;
        occupancy = 0;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "You are not the owner");
        _;
    }

    function adjustFare(uint256 newFare) public onlyOwner {
        fare = newFare;
    }

    function updateOccupancy(uint256 newOccupancy) public onlyOwner {
        occupancy = newOccupancy;
    }
}
