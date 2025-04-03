// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DynamicFareAdjustment {
    // Precision constant for converting decimal values to wei (10^18)
    uint256 public constant PRECISION = 1e18;

    // Administrator address
    address public admin;

    // Route fare mapping
    mapping(uint256 => uint256) public routeFares;

    // Route occupancy mapping
    mapping(uint256 => uint256) public routeOccupancies;

    // Event to log fare adjustments
    event FareAdjusted(uint256 indexed routeId, uint256 newFare);

    // Modifier to restrict access to administrators
    modifier onlyAdmin() {
        require(msg.sender == admin, "Only the administrator can perform this action");
        _;
    }

    // Constructor to set the administrator
    constructor() {
        admin = msg.sender;
    }

    // Function to set the predicted fare for a route (in wei)
    function setPredictedFare(uint256 routeId, uint256 fareInWei) external onlyAdmin {
        routeFares[routeId] = fareInWei;
        emit FareAdjusted(routeId, fareInWei);
    }

    // Function to set the predicted fare for a route (in decimal ETH)
    function setPredictedFareDecimal(uint256 routeId, uint256 fareInDecimal) external onlyAdmin {
        uint256 fareInWei = (fareInDecimal * PRECISION) / 1e10; // Convert decimal to wei
        routeFares[routeId] = fareInWei;
        emit FareAdjusted(routeId, fareInWei);
    }

    // Function to adjust the fare dynamically based on occupancy
    function adjustFare(uint256 routeId, uint256 occupancy) external onlyAdmin {
        uint256 currentFare = routeFares[routeId];
        uint256 fareAdjustment = (occupancy / 100) * 1e16; // Increase fare by 0.01 ETH for every 100 passengers

        if (occupancy > 100) {
            // Increase fare when occupancy is high
            routeFares[routeId] = currentFare + fareAdjustment;
        } else if (occupancy < 50 && currentFare > fareAdjustment) {
            // Decrease fare when occupancy is low (but not below 0)
            routeFares[routeId] = currentFare - fareAdjustment;
        }

        emit FareAdjusted(routeId, routeFares[routeId]);
    }

    // Function to manually adjust the fare for a route
    function manualAdjustFare(uint256 routeId, uint256 newFare) external onlyAdmin {
        routeFares[routeId] = newFare;
        emit FareAdjusted(routeId, newFare);
    }

    // Function to get the current fare for a route in wei
    function getFare(uint256 routeId) external view returns (uint256) {
        return routeFares[routeId];
    }

    // Function to get the current fare for a route in decimal ETH
    function getFareDecimal(uint256 routeId) external view returns (uint256) {
        return (routeFares[routeId] * 1e10) / PRECISION; // Convert wei to decimal
    }
}