// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DynamicFareAdjustment {
    // Precision constant for converting decimal values to wei (10^18)
    uint256 public constant PRECISION = 1e18;

    // Administrator address
    address public admin;

    // Route fare details
    struct RouteFare {
        uint256 fare; // Predicted fare in wei
        uint256 occupancy; // Current occupancy
    }

    // Mapping of route IDs to their fare details
    mapping(uint256 => RouteFare) public routes;

    // Event to log fare adjustments
    event FareAdjusted(uint256 indexed routeId, uint256 newFare);

    // Modifier to restrict access to the administrator
    modifier onlyAdmin() {
        require(msg.sender == admin, "Only the administrator can perform this action");
        _;
    }

    // Constructor to set the administrator
    constructor() {
        admin = msg.sender;
    }

    // Function to set the predicted fare for a route (in decimal, e.g., 0.3027901777605441 ETH)
    function setPredictedFare(uint256 routeId, uint256 fareInDecimal) external onlyAdmin {
        uint256 fareInWei = (fareInDecimal * PRECISION) / 1e10; // Convert decimal to wei
        routes[routeId].fare = fareInWei;
        emit FareAdjusted(routeId, fareInWei);
    }

    // Function to adjust the fare dynamically based on occupancy
    function adjustFare(uint256 routeId, uint256 occupancy) external {
        RouteFare storage route = routes[routeId];
        route.occupancy = occupancy;

        // Calculate fare adjustment based on occupancy
        uint256 baseFare = route.fare;
        uint256 adjustment = (occupancy / 100) * 1e16; // Increase fare by 0.01 ETH for every 100 passengers

        // Apply adjustment: increase fare if occupancy is high, decrease if low
        if (occupancy > 100) {
            route.fare = baseFare + adjustment;
        } else if (occupancy < 50 && baseFare > adjustment) {
            route.fare = baseFare - adjustment;
        }

        emit FareAdjusted(routeId, route.fare);
    }

    // Function for administrators to manually adjust the fare
    function manualAdjustFare(uint256 routeId, uint256 newFareInWei) external onlyAdmin {
        routes[routeId].fare = newFareInWei;
        emit FareAdjusted(routeId, newFareInWei);
    }

    // Function to get the current fare for a route in wei
    function getFare(uint256 routeId) external view returns (uint256) {
        return routes[routeId].fare;
    }

    // Function to get the current occupancy for a route
    function getOccupancy(uint256 routeId) external view returns (uint256) {
        return routes[routeId].occupancy;
    }
}