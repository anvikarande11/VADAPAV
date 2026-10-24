// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract HeirloomProtocol {
    string public ownerName;
    string public beneficiaryName;
    uint256 public threshold;
    mapping(address => bool) public guardians;
    mapping(address => bool) public hasApproved;
    uint256 public approvalCount;
    bool public recoveryTriggered;
    bool public recoveryCompleted;

    event RecoveryTriggered(string owner);
    event GuardianApproved(address guardian, uint256 currentApprovals);
    event RecoveryCompleted(string beneficiary);

    constructor(
        string memory _owner, 
        string memory _beneficiary, 
        uint256 _threshold, 
        address[] memory _guardians
    ) {
        ownerName = _owner;
        beneficiaryName = _beneficiary;
        threshold = _threshold;
        
        for(uint i = 0; i < _guardians.length; i++) {
            guardians[_guardians[i]] = true;
        }
    }

    function triggerRecovery() external {
        recoveryTriggered = true;
        emit RecoveryTriggered(ownerName);
    }

    function approveRecovery() external {
        require(recoveryTriggered, "Recovery has not been triggered yet.");
        require(guardians[msg.sender], "Caller is not an authorized guardian.");
        require(!hasApproved[msg.sender], "Guardian has already approved.");

        hasApproved[msg.sender] = true;
        approvalCount++;

        emit GuardianApproved(msg.sender, approvalCount);

        if (approvalCount >= threshold) {
            recoveryCompleted = true;
            emit RecoveryCompleted(beneficiaryName);
        }
    }
}