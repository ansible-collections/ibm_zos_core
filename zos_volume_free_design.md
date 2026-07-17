# zos_volume_free Module Reference

**Module:** `ibm.ibm_zos_core.zos_volume_free`  
**Version:** 1.0.0  
**Last Updated:** June 23, 2026

---

## Module Parameters

```yaml
parameters:
  volumes:
    description:
      - List of volume serial numbers (VOLSERs) to query
      - Can be a single volume or multiple volumes
      - Can be combined with device_numbers for union behavior
      - If neither volumes nor device_numbers specified, queries all active DASD volumes
    type: list
    elements: str
    required: false
    default: null
    examples:
      - volumes: ["USER01", "USER02"]
      - volumes: "USER01"
  
  device_numbers:
    description:
      - List of device numbers (unit addresses) to query
      - Can be a single device or multiple devices
      - Examples - "0A80", "0941", "1234"
      - Can be combined with volumes for union behavior (returns volumes matching EITHER criteria)
      - When specified, module queries all volumes then filters by device number
      - Results are deduplicated by VOLSER if a volume matches both criteria
      - Useful when you know the device number but not the VOLSER
    type: list
    elements: str
    required: false
    default: null
    examples:
      - device_numbers: ["0A80", "0A81", "0941"]
      - device_numbers: "0A80"
    
  filter:
    description:
      - Filter criteria for volume information
    type: dict
    required: false
    suboptions:
      status:
        description:
          - Filter by volume status
          - Derived from UCBSTAT flags
          - online - ucbonli=True
          - offline - ucbonli=False
          - pending - ucbchgs=True (status changing)
        type: list
        elements: str
        choices: ['online', 'offline', 'pending']
        example:
          filter:
            status: ['online']
      
      free_space_min:
        description:
          - Minimum free space threshold
          - Value is in the unit specified by 'unit' suboption (default tracks)
          - Example - if unit='tracks' and free_space_min=1000, filters volumes with >= 1000 tracks free
          - Example - if unit='cylinders' and free_space_min=100, filters volumes with >= 100 cylinders free
        type: int
        example:
          filter:
            free_space_min: 1000
      
      free_space_max:
        description:
          - Maximum free space threshold
          - Value is in the unit specified by 'unit' suboption (default tracks)
        type: int
      
      percent_free_min:
        description:
          - Minimum percentage of free space
        type: int
        example:
          filter:
            percent_free_min: 20
        
      percent_free_max:
        description:
          - Maximum percentage of free space
        type: int
      
      vtoc_indexed:
        description:
          - Filter by VTOC index status
        type: bool
        example:
          filter:
            vtoc_indexed: true
      
      unit:
        description:
          - Unit for free_space_min/max filter values
          - Does NOT affect output format (output always in tracks)
          - When 'cylinders', conversion assumes 15 tracks per cylinder (3390/3380 standard)
        type: str
        choices: ['tracks', 'cylinders']
        default: 'tracks'
        example:
          filter:
            free_space_min: 100
            unit: cylinders
```

---

## Return Values

```yaml
returns:
  volumes:
    description: List of volume information
    returned: always
    type: list
    elements: dict
    contains:
      volser:
        description: Volume serial number
        type: str
        sample: "USER01"
      
      device_number:
        description: Device number (unit address)
        type: str
        sample: "0A80"
      
      device_type:
        description: Device type
        type: str
        sample: "3390"
      
      status:
        description: Volume status (derived from device_status)
        type: str
        choices: ['online', 'offline', 'pending']
        sample: "online"
      
      total_space:
        description: Total space in tracks
        type: int
        sample: 10016
      
      free_space:
        description: Free space in tracks
        type: int
        sample: 5432
      
      used_space:
        description: Used space in tracks
        type: int
        sample: 4584
      
      percent_free:
        description: Percentage of free space
        type: float
        sample: 54.2
      
      percent_used:
        description: Percentage of used space
        type: float
        sample: 45.8
      
      total_bytes:
        description: Total space in bytes
        type: int
        sample: 567906000
      
      free_bytes:
        description: Free space in bytes
        type: int
        sample: 307609600
      
      device_status:
        description: Device status information (derived from ZOAU UCBSTAT)
        type: dict
        returned: always
        contains:
          is_online:
            description:
              - Indicates whether the device is online.
              - Derived from the z/OS UCBSTAT C(ucbonli) flag.
            type: bool
            sample: true
          
          status_changing:
            description:
              - Indicates whether the device status is currently changing.
              - Derived from the z/OS UCBSTAT C(ucbchgs) flag.
            type: bool
            sample: false
          
          is_reserved:
            description:
              - Indicates whether the device is reserved.
              - Derived from the z/OS UCBSTAT C(ucbresv) flag.
            type: bool
            sample: false
          
          is_unloaded:
            description:
              - Indicates whether the device is unloaded.
              - Derived from the z/OS UCBSTAT C(ucbunld) flag.
            type: bool
            sample: false
          
          is_allocated:
            description:
              - Indicates whether the device is allocated to a job or user.
              - Derived from the z/OS UCBSTAT C(ucbaloc) flag.
            type: bool
            sample: false
          
          is_present:
            description:
              - Indicates whether the device is present and available.
              - Derived from the z/OS UCBSTAT C(ucbpres) flag.
            type: bool
            sample: true
          
          is_system_residence:
            description:
              - Indicates whether the volume contains system residence (IPL volume).
              - Derived from the z/OS UCBSTAT C(ucbsysr) flag.
            type: bool
            sample: false
          
          is_dasd:
            description:
              - Indicates the DASD device indicator flag from UCB.
              - Derived from the z/OS UCBSTAT C(ucbdadi) flag.
            type: bool
            sample: false
      
      vtoc_info:
        description: VTOC information (from ZOAU API)
        type: dict
        returned: always
        contains:
          index_vtoc:
            description: VTOC has an index
            type: bool
            sample: true
          
          vtoc_active:
            description: VTOC index is active
            type: bool
            sample: true
          
          is_cylinder_managed:
            description:
              - Indicates whether the volume uses cylinder-managed space allocation.
              - When true, the VTOC uses cylinder boundaries for dataset allocation.
              - When false, the VTOC uses track-managed space allocation.
              - Derived from ZOAU API C(is_cylinder_managed) field.
            type: bool
            sample: false
  
  changed:
    description: Indicates if any changes were made
    returned: always
    type: bool
    sample: false
  
  failed:
    description: Indicates if the module failed
    returned: always
    type: bool
    sample: false
  
  msg:
    description: Message describing the result
    returned: always
    type: str
    sample: "Successfully retrieved volume information for 2 volumes"
```

---

## Sample Playbooks

### 1. Query All Volumes

```yaml
---
- name: Query all z/OS volumes
  hosts: zos_host
  gather_facts: false
  
  tasks:
    - name: Get information for all active DASD volumes
      ibm.ibm_zos_core.zos_volume_free:
      register: all_volumes
```

### 2. Query Specific Volumes

```yaml
---
- name: Query specific z/OS volumes
  hosts: zos_host
  gather_facts: false
  
  tasks:
    - name: Get information for specific volumes
      ibm.ibm_zos_core.zos_volume_free:
        volumes:
          - USER01
          - USER02
          - PROD01
      register: volume_info
```

### 3. Query by Device Number

```yaml
---
- name: Query volumes by device number
  hosts: zos_host
  gather_facts: false
  
  tasks:
    - name: Get volumes on specific devices
      ibm.ibm_zos_core.zos_volume_free:
        device_numbers:
          - "0A80"
          - "0A81"
          - "0941"
      register: device_volumes
```

### 4. Query by Both VOLSER and Device Number (Union)

```yaml
---
- name: Query by both VOLSER and device number
  hosts: zos_host
  gather_facts: false
  
  tasks:
    - name: Get specific volumes AND volumes on specific devices
      ibm.ibm_zos_core.zos_volume_free:
        volumes:
          - USER01
          - USER02
        device_numbers:
          - "0A80"
          - "0A81"
      register: combined_results
```

### 5. Filter by Online Status

```yaml
---
- name: Get only online volumes
  hosts: zos_host
  gather_facts: false
  
  tasks:
    - name: Query online volumes
      ibm.ibm_zos_core.zos_volume_free:
        filter:
          status: ['online']
      register: online_volumes
```

### 6. Filter by Free Space

```yaml
---
- name: Find volumes with low free space
  hosts: zos_host
  gather_facts: false
  
  tasks:
    - name: Get volumes with less than 20% free space
      ibm.ibm_zos_core.zos_volume_free:
        filter:
          percent_free_max: 20
          status: ['online']
      register: low_space_volumes
```

### 7. Filter by VTOC Index Status

```yaml
---
- name: Find volumes with indexed VTOC
  hosts: zos_host
  gather_facts: false
  
  tasks:
    - name: Get volumes with indexed and active VTOC
      ibm.ibm_zos_core.zos_volume_free:
        filter:
          vtoc_indexed: true
      register: indexed_volumes
```

### 8. Filter with Cylinder Units

```yaml
---
- name: Find volumes with at least 100 cylinders free
  hosts: zos_host
  gather_facts: false
  
  tasks:
    - name: Query volumes with minimum free cylinders
      ibm.ibm_zos_core.zos_volume_free:
        filter:
          free_space_min: 100
          unit: cylinders  # 100 cylinders = 1500 tracks
          status: ['online']
      register: volumes_with_space
```

---

## Complete Example Output

```yaml
volumes:
  - volser: "USER01"
    device_number: "0A80"
    device_type: "3390"
    status: "online"
    total_space: 10016
    free_space: 5432
    used_space: 4584
    percent_free: 54.2
    percent_used: 45.8
    total_bytes: 567906000
    free_bytes: 307609600
    device_status:
      is_online: true
      status_changing: false
      is_reserved: false
      is_unloaded: false
      is_allocated: false
      is_present: true
      is_system_residence: false
      is_dasd: true
    vtoc_info:
      index_vtoc: true
      vtoc_active: true
      is_cylinder_managed: false

changed: false
failed: false
msg: "Successfully retrieved volume information for 1 volume"
```

---

## Notes

```yaml
notes:
  - When querying by device number, the module retrieves all volumes and filters them
  - When both volumes and device_numbers are specified, returns volumes matching EITHER criteria with automatic deduplication
  - The unit parameter in filter only affects filter value interpretation. All output is always in tracks
  - The simplified status field is derived from device_status flags (pending=status_changing, online=is_online, offline=!is_online)
  - To convert tracks to cylinders, divide by 15 (for 3390/3380 devices)
