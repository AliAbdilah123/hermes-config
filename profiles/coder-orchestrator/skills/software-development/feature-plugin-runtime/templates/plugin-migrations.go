package plugins

import (
	"crypto/sha256"
	"database/sql"
	"encoding/hex"
	"fmt"
)

type Migration struct{ Plugin, ID, SQL string }

func Apply(db *sql.DB, m Migration) error {
	sum := sha256.Sum256([]byte(m.SQL))
	checksum := hex.EncodeToString(sum[:])
	tx, e := db.Begin()
	if e != nil {
		return e
	}
	defer tx.Rollback()
	var old string
	e = tx.QueryRow(`SELECT checksum FROM plugin_migrations WHERE plugin_id=? AND migration_id=?`, m.Plugin, m.ID).Scan(&old)
	if e == nil {
		if old != checksum {
			return fmt.Errorf("migration checksum drift")
		}
		return tx.Commit()
	}
	if e != sql.ErrNoRows {
		return e
	}
	if _, e = tx.Exec(m.SQL); e != nil {
		return e
	}
	if _, e = tx.Exec(`INSERT INTO plugin_migrations(plugin_id,migration_id,checksum) VALUES(?,?,?)`, m.Plugin, m.ID, checksum); e != nil {
		return e
	}
	return tx.Commit()
}
