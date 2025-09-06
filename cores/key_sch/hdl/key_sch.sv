module key_sch (
    input logic clk_i,
    input logic rst_ni,
    input logic [127:0] master_key_i,
    input logic [3:0] round_nr,
    output logic [127:0] round_key_o
);

  logic [127:0] rotated_key;
  logic [127:0] sub_key;
  reg   [127:0] prev_key;
  logic [127:0] act_key;

  logic [  7:0] rcon;


  logic [ 31:0] w0;
  logic [ 31:0] w1;
  logic [ 31:0] w2;
  logic [ 31:0] w3;

  logic [ 31:0] w0_rot;
  logic [ 31:0] w1_rot;
  logic [ 31:0] w2_rot;
  logic [ 31:0] w3_rot;

  logic [ 31:0] w0_n;
  logic [ 31:0] w1_n;
  logic [ 31:0] w2_n;
  logic [ 31:0] w3_n;

  assign w0 = prev_key[127-:32];
  assign w1 = prev_key[95-:32];
  assign w2 = prev_key[63-:32];
  assign w3 = prev_key[31-:32];

  assign w0_rot = {w0[23:0], w0[31:24]};

  assign rotated_key = {w0, w1, w2, w3_rot};

  // subbyte

  subbyte subbyte_i (
      .data_in (rotated_key),
      .data_out(sub_key)
  );

  // rcon
  always_comb begin
    case (round_nr)
      4'd1: rcon = 8'h01;
      4'd2: rcon = 8'h02;
      4'd3: rcon = 8'h04;
      4'd4: rcon = 8'h08;
      4'd5: rcon = 8'h10;
      4'd6: rcon = 8'h20;
      4'd7: rcon = 8'h40;
      4'd8: rcon = 8'h80;
      4'd9: rcon = 8'h1b;
      4'd10: rcon = 8'h36;
      default: rcon = 8'h00;
    endcase
  end

  assign w0_n = w0 ^ {rcon, 24'h0} ^ sub_key[31-:32];
  assign w1_n = w1 ^ w0_n;
  assign w2_n = w2 ^ w1_n;
  assign w3_n = w3 ^ w2_n;

  assign act_key = round_nr == 0 ? master_key_i : {w0_n, w1_n, w2_n, w3_n};
  assign round_key_o = act_key;

  always_ff @(posedge clk_i) begin : key_reg
    if (rst_ni == 0) begin
      prev_key <= '0;
    end else begin
      prev_key <= act_key;
    end
  end : key_reg

endmodule
