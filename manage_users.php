<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>User Management - Drowsiness Detection</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        }

        h1 {
            color: #333;
            margin-bottom: 10px;
        }

        .subtitle {
            color: #666;
            margin-bottom: 30px;
        }

        .action-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }

        .btn {
            padding: 10px 20px;
            border-radius: 5px;
            text-decoration: none;
            cursor: pointer;
            border: none;
            font-size: 14px;
            transition: transform 0.2s;
        }

        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
        }

        .btn-danger {
            background: #dc3545;
            color: white;
        }

        .btn-success {
            background: #28a745;
            color: white;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }

        th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px;
            text-align: left;
        }

        td {
            padding: 12px;
            border-bottom: 1px solid #e0e0e0;
        }

        tr:hover {
            background: #f8f9fa;
        }

        .form-group {
            margin-bottom: 15px;
        }

        .form-group label {
            display: block;
            margin-bottom: 5px;
            color: #555;
            font-weight: 500;
        }

        .form-group input {
            width: 100%;
            padding: 10px;
            border: 2px solid #e0e0e0;
            border-radius: 5px;
            font-size: 14px;
        }

        .form-group input:focus {
            outline: none;
            border-color: #667eea;
        }

        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
        }

        .modal.active {
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .modal-content {
            background: white;
            padding: 30px;
            border-radius: 10px;
            max-width: 500px;
            width: 90%;
        }

        .alert {
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }

        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }

        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }

        .stat-number {
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 5px;
        }

        .stat-label {
            font-size: 14px;
            opacity: 0.9;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>👥 User Management System</h1>
        <p class="subtitle">Manage users for Drowsiness Detection Application</p>

        <?php
        // Database configuration
        $host = 'localhost';
        $dbname = 'drowsiness_detection';
        $user = 'root';
        $password = ''; // Change if you have a password set

        // Connect to database
        try {
            $conn = new mysqli($host, $user, $password, $dbname);
            
            if ($conn->connect_error) {
                die("<div class='alert alert-error'>Connection failed: " . $conn->connect_error . "</div>");
            }
        } catch (Exception $e) {
            echo "<div class='alert alert-error'>Error: " . $e->getMessage() . "</div>";
            echo "<p>Please ensure WAMP is running and the database is imported.</p>";
            exit;
        }

        // Handle form submissions
        $message = '';
        $message_type = '';

        if ($_SERVER['REQUEST_METHOD'] === 'POST') {
            if (isset($_POST['add_user'])) {
                $username = $_POST['username'];
                $password = $_POST['password'];
                
                $stmt = $conn->prepare("INSERT INTO users (username, password) VALUES (?, ?)");
                $stmt->bind_param("ss", $username, $password);
                
                if ($stmt->execute()) {
                    $message = "User added successfully!";
                    $message_type = 'success';
                } else {
                    $message = "Error: " . $stmt->error;
                    $message_type = 'error';
                }
                $stmt->close();
            }

            if (isset($_POST['delete_user'])) {
                $user_id = $_POST['user_id'];
                $stmt = $conn->prepare("DELETE FROM users WHERE id = ?");
                $stmt->bind_param("i", $user_id);
                
                if ($stmt->execute()) {
                    $message = "User deleted successfully!";
                    $message_type = 'success';
                } else {
                    $message = "Error: " . $stmt->error;
                    $message_type = 'error';
                }
                $stmt->close();
            }

            if (isset($_POST['update_password'])) {
                $user_id = $_POST['user_id'];
                $new_password = $_POST['new_password'];
                
                $stmt = $conn->prepare("UPDATE users SET password = ? WHERE id = ?");
                $stmt->bind_param("si", $new_password, $user_id);
                
                if ($stmt->execute()) {
                    $message = "Password updated successfully!";
                    $message_type = 'success';
                } else {
                    $message = "Error: " . $stmt->error;
                    $message_type = 'error';
                }
                $stmt->close();
            }
        }

        // Get statistics
        $result = $conn->query("SELECT COUNT(*) as total FROM users");
        $total_users = $result->fetch_assoc()['total'];
        
        $result = $conn->query("SELECT COUNT(*) as active FROM users WHERE last_login IS NOT NULL");
        $active_users = $result->fetch_assoc()['active'];

        // Display message if exists
        if ($message) {
            echo "<div class='alert alert-$message_type'>$message</div>";
        }
        ?>

        <!-- Statistics -->
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number"><?php echo $total_users; ?></div>
                <div class="stat-label">Total Users</div>
            </div>
            <div class="stat-card">
                <div class="stat-number"><?php echo $active_users; ?></div>
                <div class="stat-label">Active Users</div>
            </div>
            <div class="stat-card">
                <div class="stat-number"><?php echo $total_users - $active_users; ?></div>
                <div class="stat-label">Inactive Users</div>
            </div>
        </div>

        <!-- Action Bar -->
        <div class="action-bar">
            <div>
                <button class="btn btn-primary" onclick="openModal('addUserModal')">➕ Add New User</button>
                <a href="http://localhost:5000" class="btn btn-success" style="margin-left: 10px;">🚀 Open App</a>
            </div>
            <div>
                <a href="http://localhost/phpmyadmin" target="_blank" class="btn btn-primary">📊 phpMyAdmin</a>
            </div>
        </div>

        <!-- Users Table -->
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Username</th>
                    <th>Registered</th>
                    <th>Last Login</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <?php
                $result = $conn->query("SELECT * FROM users ORDER BY created_at DESC");
                
                if ($result->num_rows > 0) {
                    while($row = $result->fetch_assoc()) {
                        echo "<tr>";
                        echo "<td>" . $row['id'] . "</td>";
                        echo "<td>" . htmlspecialchars($row['username']) . "</td>";
                        echo "<td>" . $row['created_at'] . "</td>";
                        echo "<td>" . ($row['last_login'] ? $row['last_login'] : 'Never') . "</td>";
                        echo "<td>";
                        echo "<button class='btn btn-primary' onclick=\"openPasswordModal(" . $row['id'] . ", '" . htmlspecialchars($row['username']) . "')\">🔑 Password</button> ";
                        echo "<form method='POST' style='display:inline;' onsubmit='return confirm(\"Are you sure you want to delete this user?\")'>";
                        echo "<input type='hidden' name='user_id' value='" . $row['id'] . "'>";
                        echo "<button type='submit' name='delete_user' class='btn btn-danger'>🗑️ Delete</button>";
                        echo "</form>";
                        echo "</td>";
                        echo "</tr>";
                    }
                } else {
                    echo "<tr><td colspan='5' style='text-align:center;padding:40px;color:#999;'>No users found. Click 'Add New User' to create one.</td></tr>";
                }
                ?>
            </tbody>
        </table>
    </div>

    <!-- Add User Modal -->
    <div id="addUserModal" class="modal">
        <div class="modal-content">
            <h2 style="margin-bottom: 20px;">Add New User</h2>
            <form method="POST">
                <div class="form-group">
                    <label>Username</label>
                    <input type="text" name="username" required>
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" name="password" required>
                </div>
                <div style="text-align: right; margin-top: 20px;">
                    <button type="button" class="btn btn-danger" onclick="closeModal('addUserModal')">Cancel</button>
                    <button type="submit" name="add_user" class="btn btn-success">Add User</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Change Password Modal -->
    <div id="passwordModal" class="modal">
        <div class="modal-content">
            <h2 style="margin-bottom: 20px;">Change Password</h2>
            <form method="POST">
                <input type="hidden" name="user_id" id="modal_user_id">
                <div class="form-group">
                    <label>Username</label>
                    <input type="text" id="modal_username" readonly style="background: #f0f0f0;">
                </div>
                <div class="form-group">
                    <label>New Password</label>
                    <input type="password" name="new_password" required>
                </div>
                <div style="text-align: right; margin-top: 20px;">
                    <button type="button" class="btn btn-danger" onclick="closeModal('passwordModal')">Cancel</button>
                    <button type="submit" name="update_password" class="btn btn-success">Update Password</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        function openModal(modalId) {
            document.getElementById(modalId).classList.add('active');
        }

        function closeModal(modalId) {
            document.getElementById(modalId).classList.remove('active');
        }

        function openPasswordModal(userId, username) {
            document.getElementById('modal_user_id').value = userId;
            document.getElementById('modal_username').value = username;
            openModal('passwordModal');
        }

        // Close modal when clicking outside
        window.onclick = function(event) {
            if (event.target.classList.contains('modal')) {
                event.target.classList.remove('active');
            }
        }
    </script>
</body>
</html>
